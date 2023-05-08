import pygame
import SimClass
from GSOF_Cockpit import SingleIndicator as SI

class Simulator(SimClass.Simulator_base):
    def _readInputs(self) -> None:
        """Sample the keys and update the variables of the car"""
        keys = pygame.key.get_pressed()
        if keys:
            if keys[pygame.K_z]:
                self.carMdl.addPower(-self.pwrRate)
                
            elif keys[pygame.K_a]:
                self.carMdl.setPower(0)

            elif keys[pygame.K_q]:
                self.carMdl.addPower(+self.pwrRate)
            
            elif keys[pygame.K_SPACE]:
                self.carMdl.setPower(0)
                self.carMdl.setVel(0)
                self.carMdl.setSteering(0)

            if keys[pygame.K_p]:
                self.carMdl.addSteering(+self.steeringRate)
                
            if keys[pygame.K_o]:
                self.carMdl.setSteering(0)

            elif keys[pygame.K_i]:
                self.carMdl.addSteering(-self.steeringRate)
            
if __name__ == "__main__":
    sim = Simulator(fps=30, size=(600,750), imageWidth=30, Cd=0.02, rollFriction=1.5)
    try:
        pygame.init()
        sim.start()
    except KeyboardInterrupt:
        sim.stop()
