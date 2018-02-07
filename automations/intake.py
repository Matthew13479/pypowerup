from magicbot import StateMachine, state
from components.intake import Intake
from automations.lifter import LifterAutomation


class IntakeAutomation(StateMachine):
    """Importing objects from other files"""
    intake: Intake
    lifter_automation: LifterAutomation

    @state(first=True, must_finish=True)
    def intake_cube(self):
        """Starts the intake motors while waiting for the cube be seen by the
        infrared sensor"""
        if self.intake.cube_inside():
            self.intake.intake_rotate(0.0)
            self.intake.extension(False)
            self.done()
        else:
            self.intake.intake_rotate(1)
            self.intake.extension(True)

    @state(must_finish=True)
    def clamp(self):
        """Grabs cube and starts lifter state machine"""
        self.intake.intake_clamp(True)
        self.intake.intake_push(False)
        self.lifter_automation.engage()
        self.done()

    @state(must_finish=True)
    def deposit(self):
        """Deposit cube."""
        self.intake.intake_rotate(-1)
        self.done()

    @state(must_finish=True)
    def stop(self):
        """Stop moving motor."""
        print("Stopping")
        self.intake.intake_rotate(0.0)
        self.done()
