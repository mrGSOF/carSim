import pygame
from modules import CarClass
from modules import SimClass
from GSOF_Cockpit import SingleIndicator as SI

class Simulator(SimClass.Simulator_base):
    def _readInputs(self) -> None:
        """Sample the keys and update the variables of the car"""
        keys = pygame.key.get_pressed()
        if keys:
            if keys[pygame.K_q]:
                self.carMdl.addAcc(-self.accRate)
                
            elif keys[pygame.K_1]:
                self.carMdl.addAcc(+self.accRate)
            
            if keys[pygame.K_p]:
                self.carMdl.addSteering(+self.steeringRate)
                
            elif keys[pygame.K_i]:
                self.carMdl.addSteering(-self.steeringRate)

            if keys[pygame.K_o]:
                self.carMdl.setSteering(0)
            
            if keys[pygame.K_z]:
                self.carMdl.setVel(0)

if __name__ == "__main__":
    pygame.init()
    sim = Simulator(fps=30, size=(600,750), imageWidth=30)
