<?xml version="1.0" encoding="UTF-8"?>
<sc id="1" name="" frequency="1" steps="0" defaultIntergreenMatrix="0">
  <sgs>
    <sg id="1" name="12" defaultSignalSequence="3">
      <defaultDurations />
    </sg>
    <sg id="2" name="13" defaultSignalSequence="3">
      <defaultDurations />
    </sg>
    <sg id="3" name="21" defaultSignalSequence="3">
      <defaultDurations />
    </sg>
    <sg id="4" name="31" defaultSignalSequence="3">
      <defaultDurations />
    </sg>
  </sgs>
  <intergreenmatrices />
  <progs>
    <prog id="1" cycletime="120000" switchpoint="0" offset="0" intergreens="0" fitness="0.000000" vehicleCount="0" name="Signal program 1">
      <sgs>
        <sg sg_id="1" signal_sequence="4">
          <cmds>
            <cmd display="3" begin="0" />
            <cmd display="1" begin="30000" />
          </cmds>
          <fixedstates />
        </sg>
        <sg sg_id="2" signal_sequence="4">
          <cmds>
            <cmd display="3" begin="30000" />
            <cmd display="1" begin="60000" />
          </cmds>
          <fixedstates />
        </sg>
        <sg sg_id="3" signal_sequence="4">
          <cmds>
            <cmd display="3" begin="60000" />
            <cmd display="1" begin="90000" />
          </cmds>
          <fixedstates />
        </sg>
        <sg sg_id="4" signal_sequence="4">
          <cmds>
            <cmd display="1" begin="0" />
            <cmd display="3" begin="90000" />
          </cmds>
          <fixedstates />
        </sg>
      </sgs>
    </prog>
  </progs>
  <stages />
  <interstageProgs />
  <stageProgs />
  <dailyProgLists />
</sc>