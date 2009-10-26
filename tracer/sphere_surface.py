# Implements spherical surface 
#
# References:
# [1] http://www.siggraph.org/education/materials/HyperGraph/raytrace/rtinter1.htm

import numpy as N
from quadric import QuadricGM

class HemisphereGM(QuadricGM):
    """
    Implements the geometry of a hemispherical surface below the xy plane (so 
    that rays going down the Z axis hit).
    """
    def __init__(self, radius=1.):
        """
        Arguments:  
        radius - Set as the sphere's radius
        Private attributes:
        _rad - radius of the sphere, a float 
        """
        QuadricGM.__init__(self)
        self.set_radius(radius)  

    def get_radius(self):
        return self._rad
    
    def set_radius(self, rad):
        if rad <= 0:
            raise ValuError("Radius must be positive")
        self._rad = rad
     
    def get_normal(self, dot, hit, c):
        """Finds the normal by taking the derivative and rotating it, returns the            
        information to the quadric class for calculations. Used by the quadrics class.      
        Arguments:                                                                      
        dot - the dot product of the normal vector and the incoming ray, used to determine 
        which side is the outer surface (this is not relevant to the paraboloid since the  
        cross product determines it, but it is to the sphere surface)                     
        hit - the coordinates of an intersection                                            
        c - the center/vertex of the surface 
        """
        normal = ((hit - c) if dot >= 0 else  (c - hit))[:,None]
        normal = normal/N.linalg.norm(normal)
        return normal

    # Ray handling protocol:
    def get_ABC(self, ray_bundle):
        """  
        Determines the variables forming the relevant quadric equation. Used by the quadrics
        class, [1]
        """ 
        d = ray_bundle.get_directions()
        v = ray_bundle.get_vertices()
        n = ray_bundle.get_num_rays()
        c = self._working_frame[:3,3]
        
        # Solve the equations to find the intersection point:
        A = (d**2).sum(axis=0)
        B = 2*(d*(v - c[:,None])).sum(axis=0)
        C = ((v - c[:,None])**2).sum(axis=0) - self.get_radius()**2
        
        return A, B, C
    
    def _select_coords(self, coords, prm):
        """
        Select from dual intersections by vetting out rays in the upper
        hemisphere, or if both are below use the default behaviour of choosing
        the first hit.
        """
        local = N.dot(N.linalg.inv(self._working_frame), N.vstack((coords.T, N.ones(2))))
        bottom_hem = (local[2,:] < 0) & (prm > 0)
        
        if not bottom_hem.any():
            return None
        if bottom_hem.sum() == 1:
            return N.where(bottom_hem)[0][0]
        return QuadricGM._select_coords(self, coords, prm)

