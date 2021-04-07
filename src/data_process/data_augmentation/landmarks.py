import math


class landmark_vector(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def length(self):
        return math.sqrt(self.x**2 + self.y**2)

    def __sub__(self, other):
        return landmark_vector(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return landmark_vector(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar):
        """
        Only for mulitply by a scalar, NOT dot product
        """
        if isinstance(scalar, landmark_vector):
            raise BaseException("This is not dot product")
        else:
            return landmark_vector(scalar*self.x, scalar*self.y)

    def __rmul__(self, scalar):
        """
        Only for mulitply by a scalar, NOT dot product
        """
        if isinstance(scalar, landmark_vector):
            raise BaseException("This is not dot product")
        else:
            return landmark_vector(scalar*self.x, scalar*self.y)

    def __str__(self):
        return "(%.2f, %.2f)"%(self.x, self.y)

    def perpendicular(self, horizontal):
        """
        Returns:
            a projection vector of self vector on the direction perpendicular to the horizontal vector
        """
        scalar = (self.x*horizontal.x + self.y*horizontal.y)/(horizontal.x**2+horizontal.y**2)
        return self - horizontal * scalar


class landmark(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __sub__(self, other):
        if isinstance(other, landmark_vector):
            return landmark(self.x - other.x, self.y - other.y)
        else:
            raise BaseException("Illegal operation")


class Landmarks(object):
    def __init__(self, landmarks):
        """
        landmarks from face_alignment"
            [pt index][2]
                       -> [x, y]

            Warning:
                pt index in the landmark figure counts from 1; however, pt index in a list counts from 0
        """
        if landmarks is not None:
            self.landmarks = landmarks[0]
        else:
            raise BaseException("No landmarks are created")

    def __getitem__(self, idx_pair):
        """
        Returns:
            landmark vector from 1st node to 2nd node specified in idx_pair
        """
        if isinstance(idx_pair, int):
            return landmark(self.landmarks[idx_pair-1][0], self.landmarks[idx_pair-1][1])
        else:
            from_idx, to_idx = idx_pair
            return landmark_vector(self.landmarks[to_idx-1][0] - self.landmarks[from_idx-1][0],\
                                   self.landmarks[to_idx-1][1] - self.landmarks[from_idx-1][1])
