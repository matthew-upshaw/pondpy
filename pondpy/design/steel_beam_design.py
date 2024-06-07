import math
import steelpy
from steelpy import aisc

class SteelBeamDesign:
    '''
    A class that represents design criteria for a steel beam according to
    AISC 360-16.

    ...

    Attributes
    ----------
    section : steelpy.steelpy.Section
        steelpy section object for the steel beam under consideration
    unbraced_length : int or float
        bending unbraced length for the major axis in inches
    yield_stress : int or float
        yield stress for the beam in ksi

    Methods
    -------
    get_moment_capacity()
        Calculates the ASD moment capacity for the steel beam under consideration.
    get_shear_capacity()
        Calculates the ASD shear capcity for the steel beam under consideration.
    '''
    def __init__(self, section, unbraced_length, yield_stress=50):
        if not isinstance(section, steelpy.steelpy.Section):
            raise TypeError('section must be a valid steelpy.steelpy.Section object')
        if not isinstance(unbraced_length, (int, float)):
            raise TypeError('unbraced_length must be non-negative int or float')
        if unbraced_length < 0:
            raise ValueError('unbraced_length must be non-negative')
        if not isinstance(yield_stress, (int, float)):
            raise TypeError('yield_stress must be a positive int or float')
        if yield_stress <= 0:
            raise ValueError('yield_stress must be positive')
        
        self.section = section
        self.unbraced_length = unbraced_length
        self.yield_stress = yield_stress

    def get_moment_capacity(self):
        '''
        Calculates the ASD moment capacity for the steel beam under consideration.

        Parameters
        ----------
        None

        Returns
        -------
        moment_capacity : float
            ASD moment capacity for the steel beam under consideration        
        '''
        if self.section.name not in aisc.profiles['W_shapes'].sections.keys():
            raise ValueError('Only W-shapes are currently supported for design.')
        else:
            # Retrieve properties from the section
            PI = math.pi
            Fy = self.yield_stress
            E = 29000
            Zx = self.section.Zx
            ry = self.section.ry
            rts = self.section.rts
            J = self.section.J
            Sx = self.section.Sx
            ho = self.section.ho
            bf = self.section.bf
            tf = self.section.tf
            tw = self.section.tw
            h = self.section.d - 2*self.section.k
            c = 1
            Lb = self.unbraced_length

            # Calculate Mn for the yielding limit state
            Mn_Y = Fy*Zx # Eq. F2-1

            # Calculate Mn for the lateral-torsional buckling limit state
            Lp = 1.76*ry*(E/Fy)**0.5 # Eq. F2-5
            Lr = 1.95*rts*(E/(0.7*Fy))*((J*c)/(Sx*ho)+(((J*c)/(Sx*ho))**2+6.76*(0.7*Fy/E)**2)**0.5)**0.5 # Eq. F2-6

            if Lb <= Lp:
                # Lateral-torsional-buckling does not apply
                Mn_LTB = Mn_Y
            elif Lp < Lb <= Lr:
                Mn_LTB = min(Mn_Y - (Mn_Y-0.7*Fy*Sx)*((Lb-Lp)/(Lr-Lp)), Mn_Y)
            else:
                Fcr = (PI**2*E)/((Lb/rts)**2)*(1+0.078*(J*c)/(Sx*ho)*(Lb/rts)**2)**0.5
                Mn_LTB = min(Fcr*Sx, Mn_Y)

            if (bf/2)/tf > 0.38*(E/Fy)**0.5:
                # Section is noncompact or slender --> Consider compression flange local buckling
                lambda_pf = 0.38*(E/Fy)**0.5
                lambda_rf = 1.0*(E/Fy)**0.5
                lambda_f = (bf/2)/tf

                if lambda_f <= lambda_rf:
                    # Section is noncompact
                    Mn_FLB = Mn_Y - (Mn_Y - 0.7*Fy*Sx)*(lambda_f-lambda_pf)/(lambda_rf-lambda_pf) # Eq. F3-1
                else:
                    # Section is slender --> No current W-Shapes are slender
                    '''kc = 4/((h/tw)**0.5)
                    if kc < 0.35:
                        kc = 0.35
                    elif kc > 0.76:
                        kc = 0.76
                    
                    Mn_FLB = (0.9*E*kc*Sx)/(lambda_f**2) # Eq. F3-2'''

            else:
                Mn_FLB = Mn_Y

            return (min(Mn_Y, Mn_LTB, Mn_FLB)/12)/1.67
    
    def get_shear_capacity(self):
        '''
        Calculates the ASD shear capcity for the steel beam under consideration.

        Parameters
        ----------
        None

        Returns
        -------
        shear_capacity : float
             ASD shear capcity for the steel beam under consideration
        '''
        if self.section.name not in aisc.profiles['W_shapes'].sections.keys():
            raise ValueError('Only W-shapes are currently supported for design.')
        else:
            # Retrieve properties from the section
            Fy = self.yield_stress
            E = 29000
            h = self.section.d - 2*self.section.k
            tw = self.section.tw
            d = self.section.d
            kv = 5.34

            if (h/tw) <= 2.24*(E/Fy)**0.5:
                omega_v = 1.5
                Cv1 = 1.0 # Eq. G2-2
            elif (h/tw) <= 1.10*(kv*E/Fy)**0.5:
                omega_v = 1.67
                Cv1 = 1.0 # Eq. G2-3
            else:
                omega_v = 1.67
                Cv1 = (1.10*(kv*E/Fy)**0.5)/(h/tw) #Eq. G2-4

            Vn = 0.6*Fy*(d*tw)*Cv1 # Eq. G2-1

            return (Vn/omega_v)
