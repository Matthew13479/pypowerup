from magicbot import StateMachine, state, timed_state
from components.intake import Intake
from components.lifter import Lifter


class IntakeAutomation(StateMachine):
    intake: Intake
    lifter: Lifter

    def on_enable(self):
        if not self.intake.arms_out:
            self.engage(initial_state="start")

    @timed_state(must_finish=True, duration=0.5, next_state="stop")
    def start(self):
        """Get the intake arms out of their starting position."""
        self.intake.extend(True)
        self.intake.rotate(1)
        self.intake.arms_out = True

    @state(first=True, must_finish=True)
    def intake_cube(self, state_tm):
        """Start the intake motors and wait for the cube to fall into the containment mechanism."""
        self.intake.rotate(-1)
        self.intake.extend(True)
        self.intake.clamp(False)
        self.intake.push(False)
        if self.intake.is_cube_contained() and state_tm > 0.2:
            self.next_state("pulling_in_cube")

    @timed_state(must_finish=True, duration=0.5, next_state="grab_cube")
    def pulling_in_cube(self):
        self.intake.extend(False)
        self.intake.rotate(-1)

    @state(must_finish=True)
    def grab_cube(self, state_tm):
        self.intake.clamp(True)
        self.intake.push(False)
        if state_tm > 0.01:
            self.lifter.move(0.1)
            self.intake.extend(False)
        self.next_state("stop")

    @state(must_finish=True)
    def exchange(self):
        self.intake.rotate(1)
        self.intake.push(True)
        self.intake.clamp(False)
        if not self.intake.is_cube_contained():
            self.next_state("push_out_cube")

    @timed_state(must_finish=True, duration=0.5, next_state="stop")
    def push_out_cube(self):
        self.intake.rotate(1)
        self.intake.extend(False)
        self.intake.push(False)

    @timed_state(must_finish=True, duration=0.2, next_state="reset_containment")
    def eject_cube(self):
        self.intake.clamp(False)
        self.intake.push(True)

    @state(must_finish=True)
    def reset_containment(self):
        self.intake.clamp(False)
        self.intake.push(False)
        self.done()

    @state(must_finish=True)
    def stop(self):
        """Stop moving motor."""
        self.intake.rotate(0)
        self.intake.extend(False)
        self.done()
