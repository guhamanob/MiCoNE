"""
    Module containing tests for the Otu class
"""

import numpy as np
import pytest

from mindpipe.main import Otu


@pytest.mark.usefixtures("biom_data", "biom_files", "tsv_files", "stool_biom")
class TestOtu:
    """ Tests for the Otu class """

    def test_init(self, biom_data):
        for biom in biom_data:
            otu_inst = Otu(biom)
            assert (otu_inst.otu_data.to_dataframe() == biom.to_dataframe()).any().any()

    def test_load_data_biom(self, biom_files):
        for biom in biom_files["good"]:
            otu_inst = Otu.load_data(biom)
            assert hasattr(otu_inst, "otu_data")
            assert hasattr(otu_inst, "sample_metadata")
            assert hasattr(otu_inst, "obs_metadata")

    def test_load_data_tsv(self, tsv_files):
        for otu, sample, tax in tsv_files["good"]:
            otu_inst = Otu.load_data(otu, sample, tax, dtype="tsv")
            assert hasattr(otu_inst, "otu_data")
            assert hasattr(otu_inst, "sample_metadata")
            assert hasattr(otu_inst, "obs_metadata")

    def test_normalize(self, stool_biom):
        otu_inst = Otu(stool_biom)
        sample_norm = otu_inst.normalize()
        assert (otu_inst.otu_data.to_dataframe().sum(axis=0) > 1).all()
        assert np.isclose(sample_norm.otu_data.to_dataframe().sum(axis=0), 1.0).all()
        assert sample_norm.is_norm(axis='sample')
        obs_norm = otu_inst.normalize(axis='observation')
        assert (otu_inst.otu_data.to_dataframe().sum(axis=1) > 1).all()
        assert obs_norm.is_norm(axis='observation')
        assert np.isclose(obs_norm.otu_data.to_dataframe().sum(axis=1), 1.0).all()
        with pytest.raises(ValueError):
            otu_inst.normalize(method='random_method')
        with pytest.raises(NotImplementedError):
            otu_inst.normalize(method='css')
        with pytest.raises(NotImplementedError):
            otu_inst.normalize(method='rarefy')

    def test_rm_sparse_samples(self, stool_biom):
        otu_inst = Otu(stool_biom)
        rm_samples_otu = otu_inst.rm_sparse_samples()
        assert otu_inst.otu_data.shape[0] == rm_samples_otu.otu_data.shape[0]
        assert otu_inst.otu_data.shape[1] > rm_samples_otu.otu_data.shape[1]
        assert otu_inst.otu_data.shape[1] - rm_samples_otu.otu_data.shape[1] == 1
        norm_otu = otu_inst.normalize()
        with pytest.raises(ValueError):
            norm_otu.rm_sparse_samples()

    def test_rm_sparse_obs(self, stool_biom):
        otu_inst = Otu(stool_biom)
        rm_obs_otu = otu_inst.rm_sparse_obs(prevalence_thres=0.4)
        print(rm_obs_otu.otu_data.data("otu_merged", axis="observation"))
        assert otu_inst.otu_data.shape[1] == rm_obs_otu.otu_data.shape[1]
        assert otu_inst.otu_data.shape[0] >= rm_obs_otu.otu_data.shape[0]
        assert otu_inst.otu_data.shape[0] - rm_obs_otu.otu_data.shape[0] == 10
