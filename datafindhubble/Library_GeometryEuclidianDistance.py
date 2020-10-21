import numpy
"""
Computes the Euclidean distance between two n-vectors ``Point1`` and ``Point2``,
which is defined as

.. math::

   {||Point1-Point2||}_2

Parameters
----------
Point1 : ndarray
    An :math:`n`-dimensional vector.
Point2 : ndarray
    An :math:`n`-dimensional vector.

Returns
-------
d : double
    The Euclidean distance between vectors ``Point1`` and ``Point2``.
"""
def Main(Point1 = None, Point2 = None):
	return numpy.linalg.norm(numpy.array(Point1) - numpy.array(Point2))
