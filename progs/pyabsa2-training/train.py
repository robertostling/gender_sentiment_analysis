from pprint import pprint

from pyabsa import AspectPolarityClassification as APC
from pyabsa import ModelSaveOption, DeviceTypeOption
from pyabsa import DatasetItem

dataset = DatasetItem("erc_custom_eng",
        ["natalia_eng", # Natalia's annotated English data
            "102.Chinese", "130.Chinese_Zhang", # All available Chinese
            # Mixed product reviews (102), restaurant reviews (130)
            "126.russian", # All available Russian, restaurant reviews
            "124.english", # Restaurant reviews, similar to Russian data
            "129.Kaggle", # fairly long sentences, tech reviews
            "109.MAMS", # restaurant reviews
            "101.ACL_Twitter", # lots of humans
            "110.SemEval", # tech/restaurant reviews
            "121.MOOC_En", # MOOC reviews, some humans
            #"117.Television", # short tech reviews

            ])

config = APC.APCConfigManager.get_apc_config_multilingual()
config.num_epoch = 1
config.model = APC.APCModelList.FAST_LSA_T_V2
trainer = APC.APCTrainer(
    config=config,
    dataset=dataset,
    # Apparently this is not recommended:
    #from_checkpoint="multilingual",
    auto_device=DeviceTypeOption.AUTO,
    path_to_save=None,
    checkpoint_save_mode=ModelSaveOption.SAVE_MODEL_STATE_DICT,
    load_aug=False,
    # there are some augmentation dataset for integrated datasets, you use them by setting load_aug=True to improve performance
)


