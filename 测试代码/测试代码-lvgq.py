import spcm
from spcm import units
with spcm.Card('/dev/spcm0') as card:
    is_demo = card.is_demo_card()
    print(f"Is demo card: {is_demo}")
    product_name = card.product_name()  # 获取产品名称
    print(product_name)

    # # 设置card为DDS
    # card.card_mode(spcm.SPC_REP_STD_DDS)
    # # 开启通道
    # channels = spcm.Channels(card)  # enable all channels
    # channels.enable(True)
    # channels.output_load(50 * units.ohm)
    # channels.amp(500 * units.mV)
    # card.write_setup()
    #
    # # 设置DDS
    # dds = spcm.DDS(card, channels=channels)
    # dds.reset()
    # # 设置DDS参数
    # num_cores = len(dds)
    # for core in dds:
    #     core.amp(40 * units.percent / num_cores)
    #     core.freq(5 * units.MHz + int(core) * 5 * units.MHz)
    # # 固定 要写
    # dds.exec_at_trg()
    # dds.write_to_card()
    # # 开启card
    # card.start(spcm.M2CMD_CARD_ENABLETRIGGER, spcm.M2CMD_CARD_FORCETRIGGER)
    #
