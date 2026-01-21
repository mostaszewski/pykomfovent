import pytest

from pykomfovent.parser import KomfoventParseError, parse_state

MAIN_XML = (
    b'<?xml version="1.0" encoding="windows-1250"?> <A><OMO>NORMALNY      </OMO>'
    b"<AI0>20.9 \xb0C  </AI0><AI1>23.2 \xb0C  </AI1><AI2>5.4 \xb0C   </AI2>"
    b"<SP>50 </SP><SAF>50 %              </SAF><EAF>50 %              </EAF>"
    b"<SAFS>50 %              </SAFS><EAFS>50 %              </EAFS>"
    b"<FCG>47 %  </FCG><EC1>87 %  </EC1><EC2> 305 W   </EC2><EC3>64 W     </EC3>"
    b"<EC4>0 W      </EC4><EC5A>0.41        </EC5A><EC5D>0.35        </EC5D>"
    b"<EC6D>1.21 kWh    </EC6D><EC6M>42.13 kWh   </EC6M><EC6T>204.73 kWh  </EC6T>"
    b"<EC7D>0.00 kWh    </EC7D><EC7M>0.00 kWh    </EC7M><EC7T>0.04 kWh    </EC7T>"
    b"<EC8D>3.24 kWh    </EC8D><EC8M>184.41 kWh  </EC8M><EC8T>1285.67 kWh </EC8T>"
    b"<ST>21.0 \xb0C  </ST><ET>--.- \xb0C  </ET><AQS>--.- %    </AQS>"
    b"<AQ>25 %      </AQ><AHS>--.- %    </AHS><AH>25 %      </AH>"
    b"<VF>203571212 </VF></A>"
)

DETAIL_XML = (
    b'<?xml version="1.0" encoding="windows-1250"?> <V>'
    b"<ST>20.7 \xb0C  </ST><ET>23.2 \xb0C  </ET><OT>5.3 \xb0C   </OT>"
    b"<WT>**.* \xb0C  </WT><PT1>21.9 \xb0C  </PT1><PT2>**.* \xb0C  </PT2>"
    b"<PH1>25 %  </PH1><PH2>**.* %</PH2><SF>50 %              </SF>"
    b"<EF>50 %              </EF><SP>0 mV     </SP><EP>0 mV     </EP>"
    b"<SFI>50 % </SFI><EFI>50 % </EFI><S1>**.* mV  </S1><S2>**.* mV  </S2>"
    b"<HE>6 %  </HE><WC>0 %  </WC><EH>0 %  </EH><DX>0 %  </DX><AD>100 %</AD>"
    b"<FC>47 %  </FC><ES>100 % </ES><OH>#.## g/m3            </OH>"
    b"<IH>4.82 g/m3            </IH><EXT>20.4 \xb0C  </EXT></V>"
)


def test_parse_state() -> None:
    state = parse_state(MAIN_XML, DETAIL_XML)

    assert state.mode == "NORMALNY"
    assert state.supply_temp == 20.9
    assert state.extract_temp == 23.2
    assert state.outdoor_temp == 5.4
    assert state.supply_temp_setpoint == 21.0
    assert state.extract_temp_setpoint is None
    assert state.supply_fan_percent == 50.0
    assert state.extract_fan_percent == 50.0
    assert state.supply_fan_intensity == 50.0
    assert state.extract_fan_intensity == 50.0
    assert state.heat_exchanger_percent == 6.0
    assert state.electric_heater_percent == 0.0
    assert state.filter_contamination == 47.0
    assert state.heat_exchanger_efficiency == 87.0
    assert state.heat_recovery_power == 305.0
    assert state.power_consumption == 64.0
    assert state.heating_power == 0.0
    assert state.spi_actual == 0.41
    assert state.spi_daily == 0.35
    assert state.energy_consumed_daily == 1.21
    assert state.energy_consumed_monthly == 42.13
    assert state.energy_consumed_total == 204.73
    assert state.energy_heating_daily == 0.0
    assert state.energy_heating_monthly == 0.0
    assert state.energy_heating_total == 0.04
    assert state.energy_recovered_daily == 3.24
    assert state.energy_recovered_monthly == 184.41
    assert state.energy_recovered_total == 1285.67
    assert state.air_quality == 25.0
    assert state.humidity == 25.0
    assert state.flags == 203571212


def test_parse_invalid_xml() -> None:
    with pytest.raises(KomfoventParseError):
        parse_state(b"not xml", DETAIL_XML)


def test_parse_empty_values() -> None:
    main = b'<?xml version="1.0" encoding="windows-1250"?> <A><OMO></OMO><VF></VF></A>'
    detail = b'<?xml version="1.0" encoding="windows-1250"?> <V></V>'
    state = parse_state(main, detail)
    assert state.mode == ""
    assert state.flags == 0
    assert state.supply_temp is None
