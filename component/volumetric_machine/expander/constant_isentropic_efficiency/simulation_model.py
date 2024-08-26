from component.base_component import BaseComponent
from connector.mass_connector import MassConnector
from connector.work_connector import WorkConnector
from connector.heat_connector import HeatConnector

from CoolProp.CoolProp import PropsSI
# from scipy.optimize import fsolve
import numpy as np
import time

class ExpanderCstEff(BaseComponent):
    def __init__(self):
        super().__init__()
        self.su = MassConnector()
        self.ex = MassConnector() # Mass_connector
        self.work_exp = WorkConnector()

    def clear_intermediate_states(self):
        """Clear all intermediate states by resetting the connectors."""
        self.su.reset()
        self.ex.reset()

    def get_required_inputs(self):

        "This is a temporary fix to the problem"
        # Always get fresh values from the connectors
        inputs = {}
        if self.su.fluid is not None:
            inputs['su_fluid'] = self.su.fluid
        if self.su.T is not None:
            inputs['su_T'] = self.su.T
        elif self.su.h is not None:
            inputs['su_h'] = self.su.h
        if self.su.p is not None:
            inputs['su_p'] = self.su.p
        if self.ex.p is not None:
            inputs['ex_p'] = self.ex.p

        # Now update the internal inputs dictionary
        self.inputs = inputs

        # if self.inputs == {}:
        #     if self.su.fluid is not None:
        #         self.inputs['su_fluid'] = self.su.fluid
        #     if self.su.T is not None:
        #         self.inputs['su_T'] = self.su.T
        #     elif self.su.h is not None:
        #         self.inputs['su_h'] = self.su.h
        #     if self.su.p is not None:
        #         self.inputs['su_p'] = self.su.p
        #     if self.ex.p is not None:
        #         self.inputs['ex_p'] = self.ex.p
        
        # if self.inputs != {}:
        #     self.su.set_fluid(self.inputs['su_fluid'])
        #     if 'su_T' in self.inputs:
        #         self.su.set_T(self.inputs['su_T'])
        #     elif 'su_h' in self.inputs:
        #         self.su.set_h(self.inputs['su_h'])
        #     if 'su_p' in self.inputs:
        #         self.su.set_p(self.inputs['su_p'])
        #     if 'ex_p' in self.inputs:
        #         self.ex.set_p(self.inputs['ex_p'])

        return ['su_p', 'su_T', 'ex_p', 'su_fluid']
    
    def get_required_parameters(self):
        return [
            'eta_is',
        ]
    
    def print_setup(self):
        print("=== Expander Setup ===")
        print("Connectors:")
        print(f"  - su: fluid={self.su.fluid}, T={self.su.T}, p={self.su.p}, m_dot={self.su.m_dot}")
        print(f"  - ex: fluid={self.ex.fluid}, T={self.ex.T}, p={self.ex.p}, m_dot={self.ex.m_dot}")


        print("\nInputs:")
        for input in self.get_required_inputs():
            if input in self.inputs:
                print(f"  - {input}: {self.inputs[input]}")
            else:
                print(f"  - {input}: Not set")


        print("\nParameters:")
        for param in self.get_required_parameters():
            if param in self.params:
                print(f"  - {param}: {self.params[param]}")
            else:
                print(f"  - {param}: Not set")

        print("======================")

    def solve(self):
        self.check_calculable()
        self.check_parametrized()
        # print('Je rentre dans lexpanseur')
        if self.calculable and self.parametrized:
            print('Inlet expander')
            print(self.su.print_resume())
            try:
                # print('P_su_exp = ', self.su.p)
                h_ex_is = PropsSI('H', 'P', self.ex.p, 'S', self.su.s, self.su.fluid)
                h_ex = self.su.h - (self.su.h - h_ex_is) / self.params['eta_is']
                self.ex.set_h(h_ex)
                self.ex.set_fluid(self.su.fluid)
                # self.ex.set_p(self.ex.p)
                self.ex.set_m_dot(self.su.m_dot)
                # print('P_ex_exp = ', self.ex.p)

                self.defined = True
            except:
                print('Convergence error in expander model')
                self.defined = False
            print('Outlet expander')
            print(self.ex.print_resume())

    def print_results(self):
        print("=== Expander Results ===")
        print("Connectors:")
        print(f"  - su: fluid={self.su.fluid}, T={self.su.T}, p={self.su.p}, m_dot={self.su.m_dot}")
        print(f"  - ex: fluid={self.ex.fluid}, T={self.ex.T}, p={self.ex.p}, m_dot={self.ex.m_dot}")

        print("\nResults:")
        print(f"  - h_ex: {self.ex.h}")
        print(f"  - T_ex: {self.ex.T}")
        print("=========================")
