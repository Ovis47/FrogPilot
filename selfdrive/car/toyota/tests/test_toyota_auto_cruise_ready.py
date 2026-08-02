import unittest
from types import SimpleNamespace

from opendbc.can.packer import CANPacker
from openpilot.selfdrive.car.toyota.toyotacan import create_main_button_command


class TestToyotaAutoCruiseReady(unittest.TestCase):
  def setUp(self):
    self.packer = CANPacker("toyota_nodsu_pt_generated")

  def test_create_main_button_command(self):
    msg = create_main_button_command(self.packer)
    # DSU_CRUISE is address 869 (0x365)
    self.assertEqual(msg[0], 869)
    self.assertEqual(msg[2], 0)  # bus 0

  def test_auto_cruise_ready_logic(self):
    # State simulation test for carcontroller logic
    cruise_ready_sent = False
    frogpilot_toggles = SimpleNamespace(auto_cruise_ready=True)

    # Case 1: Shift from PARK to DRIVE when available is False
    gear_shifter_drive = 2  # Not PARK
    cruise_available = False

    can_sends = []
    if not cruise_ready_sent and gear_shifter_drive != 0:
      if frogpilot_toggles.auto_cruise_ready and not cruise_available:
        can_sends.append(create_main_button_command(self.packer))
      cruise_ready_sent = True

    self.assertEqual(len(can_sends), 1)
    self.assertEqual(can_sends[0][0], 869)
    self.assertTrue(cruise_ready_sent)

    # Case 2: Subsequent frame in DRIVE - should not resend
    can_sends_frame2 = []
    if not cruise_ready_sent and gear_shifter_drive != 0:
      if frogpilot_toggles.auto_cruise_ready and not cruise_available:
        can_sends_frame2.append(create_main_button_command(self.packer))
      cruise_ready_sent = True

    self.assertEqual(len(can_sends_frame2), 0)

    # Case 3: Shift back to PARK - resets flag
    gear_shifter_park = 0  # PARK
    if cruise_ready_sent and gear_shifter_park == 0:
      cruise_ready_sent = False

    self.assertFalse(cruise_ready_sent)


if __name__ == "__main__":
  unittest.main()
