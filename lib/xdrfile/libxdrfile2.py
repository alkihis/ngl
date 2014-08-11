# This file was automatically generated by SWIG (http://www.swig.org).
# Version 2.0.11
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.




"""

:Author:  Oliver Beckstein <orbeckst@gmail.com>
:Author:  Manuel Melo <manuel.nuno.melo@gmail.com>
:Year:    2014
:Licence: GNU GENERAL PUBLIC LICENSE Version 2 (or higher)


The Gromacs XTC/TRR library :mod:`libxdrfile2`
==============================================

:mod:`libxdrfile2`, a derivative of the Gromacs_ `libxdrfile library`_, provides an
interface to some high-level functions for XTC/TRR trajectory handling.
Only functions required for reading and processing whole trajectories are exposed at
the moment; low-level routines to read individual numbers are not provided. In
addition, :mod:`libxdrfile2` exposes functions to allow fast frame indexing and XDR
file seeking.

The functions querying the numbers of atoms in a trajectory frame
(:func:`read_xtc_natoms` and :func:`read_trr_natoms`) open a file themselves and
only require the file name.

All other functions operate on a *XDRFILE* object, which is a special file
handle for xdr files.  Any xdr-based trajectory file (XTC or TRR format) always
has to be opened with :func:`xdrfile_open`. When done, close the trajectory
with :func:`xdrfile_close`.

The functions fill or read existing arrays of coordinates; they never allocate
these arrays themselves. Hence they need to be setup outside libxdrfile2 as
numpy arrays. The exception to these are the indexing ones functions that take
care of array allocation and transference to a garbage-collectable memory object.


.. _Gromacs: http://www.gromacs.org
.. _libxdrfile library: http://www.gromacs.org/Developer_Zone/Programming_Guide/XTC_Library

.. versionchanged:: 0.8.0
   :mod:`libxdrfile2` is now used instead of :mod:`libxdrfile`. :mod:`libxdrfile2` is
   based on :mod:`libxdrfile` but has xdr seeking and indexing capabilities.
   Unlike :mod:`libxdrfile` before it, :mod:`libxdrfile2` is distributed under the GNU
   GENERAL PUBLIC LICENSE, version 2 (or higher).


Example: Reading from a XTC
---------------------------

In the example we read coordinate frames from an existing XTC trajectory::

  import numpy as np
  from libxdrfile2 import xdrfile_open, xdrfile_close, read_xtc_natoms, read_xtc, DIM, exdrOK
  xtc = 'md.xtc'
  
  # get number of atoms
  natoms = read_xtc_natoms(xtc)

  # allocate coordinate array of the right size and type
  # (the type float32 is crucial to match the underlying C-code!!)
  x = np.zeros((natoms, DIM), dtype=np.float32)
  # allocate unit cell box
  box = np.zeros((DIM, DIM), dtype=np.float32)

  # open file
  XTC = xdrfile_open(xtc, 'r')

  # loop through file until return status signifies end or a problem
  # (it should become exdrENDOFFILE on the last iteration)
  status = exdrOK
  while status == exdrOK:
     status,step,time,prec = read_xtc(XTC, box, x)
     # do something with x
     centre = x.mean(axis=0)
     print 'Centre of geometry at %(time)g ps: %(centre)r' % vars()

  # finally close file
  xdrfile_close(XTC)

Note that only the *contents* of the coordinate and unitcell arrays *x* and
*box* change.


Functions and constants
-----------------------

The module defines a number of constants such as :data:`DIM` or the
`Status symbols`_.

.. data:: DIM

          The number of cartesian dimensions for which the underlying C-code
          was compiled; this is most certainly 3.


Status symbols
~~~~~~~~~~~~~~

A number of symbols are exported; they all start with the letters
``exdr``. Important ones are listed here:

.. data:: exdrOK

          Success of xdr file read/write operation.

.. data:: exdrCLOSE
 
          xdr file is closed

.. data:: exdrENDOFFILE

          end of file was reached (response of :func:`read_xtc` and
          :func:`read_trr` after the last read frame)

.. data:: exdrFILENOTFOUND

          :func:`xdrfile_open` cannot find the requested file


Opening and closing of XDR files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Two low-level functions are used to obtain a *XDRFILE* object (a file handle)
to access xdr files such as XTC or TRR trajectories.

.. function:: xdrfile_open(path, mode) -> XDRFILE

              Open *path* and returns a *XDRFILE* handle that is required by other
              functions.

              :Arguments:
		  *path*
		     file name
		  *mode*
		     'r' for reading and 'w' for writing
	      :Returns: *XDRFILE* handle

.. function:: xdrfile_close(XDRFILE) -> status

              Close the xdrfile pointed to by *XDRFILE*. 

              .. Warning:: Closing an already closed file will lead to a 
                           crash with a double-free pointer error.

XTC functions
~~~~~~~~~~~~~

The XTC trajectory format is a lossy compression format that only stores
coordinates. Compression level is determined by the *precision* argument to the
:func:`write_xtc` function. Coordinates (Gromacs_ uses nm natively) are
multiplied by *precision* and truncated to the integer part. A typical value is
1000.0, which gives an accuracy of 1/100 of an Angstroem.

The advantage of XTC over TRR is its significantly reduced size.


.. function:: read_xtc_natoms(fn) -> natoms

              Read the number of atoms *natoms* from a xtc file *fn*.

              :Arguments:
                *fn*
                   file name of an xtc file

              :Raises: :exc:`IOError` if the supplied filed is not a XTC 
                       or if it is not readable.

.. function:: read_xtc_numframes(fn) -> (numframes, offsets)

              Read through the whole trajectory headers to obtain the total number of frames. 
              The process is speeded up by reading frame headers for the amount of data in the frame,
              and then skipping directly to the next header. An array of frame offsets is also
              returned, which can later be used to seek direcly to arbitrary frames in the trajectory. 

              :Arguments:
                *fn*
                   file name of an xtc file

              :Returns:
                a tuple containing:
                  *numframes*
                     an int with the total frame count in the trajectory
                  *offsets*
                     a numpy array of int64 recording the starting byte offset of each frame

              :Raises: :exc:`IOError` if the supplied filed is not a XTC 
                       or if it is not readable.

.. function:: read_xtc(XDRFILE, box, x) -> (status, step, time, precision)

              Read the next frame from the opened xtc trajectory into *x*.

              :Arguments:
                *XDRFILE*
                   open *XDRFILE* object
                *box*
                   pre-allocated numpy ``array((DIM,DIM),dtype=numpy.float32)`` which
                   is filled with the unit cell box vectors
                *x*
                   pre-allocated numpy ``array((natoms, DIM),dtype=numpy.float32)``
                   which is updated with the coordinates from the frame

              :Returns:
                a tuple containing:
                  *status*
                     integer status (0 = exdrOK), see `Status symbols`_ for other
                     values)
                  *step*
                     simulation step
                  *time*
                     simulation time in ps
                  *precision*
                     precision of the lossy xtc format (typically 1000.0)

.. function:: write_xtc(XDRFILE, step, time, box, x, prec) -> status

              Write the next frame *x* to the opened xtc trajectory.

              :Arguments:
                *XDRFILE*
                   open *XDRFILE* object (writable)
                *step*
                   simulation step
                *time*
                   time step in ps
                *box*
                   numpy ``array((DIM,DIM),dtype=numpy.float32)`` which contains 
                   the unit cell box vectors
                *x*
                   numpy ``array((natoms, DIM),dtype=nump.float32)``
                   which contains the coordinates from the frame
                *precision*
                   precision of the lossy xtc format (typically 1000.0)

              :Returns: *status*, integer status (0 = OK), see the ``libxdrfile2.exdr*`` 
                        constants under `Status symbols`_ for other values)

TRR functions
~~~~~~~~~~~~~

TRR is the Gromacs_ native full-feature trajectory storage format. It can contain position 
coordinates, velocities and forces, and the lambda value for free energy perturbation 
calculations. Velocities and forces are optional in the sense that they can be all zero.

.. function:: read_trr_natoms(fn) -> natoms

              Read the number of atoms *natoms* from a trr file *fn*.

              :Arguments:
                *fn*
                   file name of a trr file

              :Raises: :exc:`IOError` if the supplied filed is not a TRR
                       or if it is not readable.

.. function:: read_trr_numframes(fn) -> (numframes, offsets)

              Read through the whole trajectory headers to obtain the total number of frames. 
              The process is speeded up by reading frame headers for the amount of data in the frame,
              and then skipping directly to the next header. An array of frame offsets is also
              returned, which can later be used to seek direcly to arbitrary frames in the trajectory. 

              :Arguments:
                *fn*
                   file name of an xtc file

              :Returns:
                a tuple containing:
                  *numframes*
                     an int with the total frame count in the trajectory
                  *offsets*
                     a numpy array of int64 recording the starting byte offset of each frame

              :Raises: :exc:`IOError` if the supplied filed is not a TRR or if it is not readable.

.. function:: read_trr(XDRFILE, box, x, v, f) -> (status, step, time, lambda)

              Read the next frame from the opened trr trajectory into *x*, *v*, and *f*.

              :Arguments:
                *XDRFILE*
                   open *XDRFILE* object
                *box*
                   pre-allocated numpy ``array((DIM,DIM),dtype=numpy.float32)`` which
                   is filled with the unit cell box vectors
                *x*
                   pre-allocated numpy ``array((natoms, DIM),dtype=nump.float32)``
                   which is updated with the **coordinates** from the frame
                *v*
                   pre-allocated numpy ``array((natoms, DIM),dtype=nump.float32)``
                   which is updated with the **velocities** from the frame
                *f*
                   pre-allocated numpy ``array((natoms, DIM),dtype=nump.float32)``
                   which is updated with the **forces** from the frame

              :Returns:
                a tuple containing:
                  *status*
                     integer status (0 = exdrOK), see the ``libxdrfile2.exdr*`` constants 
                     under `Status symbols`_ for other values)
                  *step*
                     simulation step
                  *time*
                     simulation time in ps
                  *lambda*
                     current lambda value (only interesting for free energy perturbation)
                  *has_x*
                     boolean indicating whether coordinates were read from the TRR
                  *has_v*
                     boolean indicating whether velocities were read from the TRR
                  *has_f*
                     boolean indicating whether forces were read from the TRR

.. function:: write_trr(XDRFILE, step, time, lambda, box, x, v, f) -> status

              Write the next frame to the opened trr trajectory.

              :Arguments:
                *XDRFILE*
                   open *XDRFILE* object (writable)
                *step*
                   simulation step
                *time*
                   time step in ps
                *lambda*
                   free energy lambda value (typically 0.0)
                *box*
                   numpy ``array((DIM,DIM),dtype=numpy.float32)`` which contains 
                   the unit cell box vectors
                *x*
                   numpy ``array((natoms, DIM),dtype=nump.float32)``
                   which contains the **coordinates** from the frame
                *v*
                   numpy ``array((natoms, DIM),dtype=nump.float32)``
                   which contains the **velocities** from the frame
                *f*
                   numpy ``array((natoms, DIM),dtype=nump.float32)``
                   which contains the **forces** from the frame

              .. versionchanged:: 0.8.0
                   either one of *x*, *v*, or *f* can now be set as a natom,0-DIM
                   numpy ``array((natom, 0),dtype=nump.float32)``. This will cause the
                   corresponding property to be skipped when writing to file.
 
              :Returns: *status*, integer status (0 = OK), see the ``libxdrfile2.exdr*`` 
                        constants under `Status symbols`_ for other values)


"""


from sys import version_info
if version_info >= (2,6,0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_libxdrfile2', [dirname(__file__)])
        except ImportError:
            import _libxdrfile2
            return _libxdrfile2
        if fp is not None:
            try:
                _mod = imp.load_module('_libxdrfile2', fp, pathname, description)
            finally:
                fp.close()
            return _mod
    _libxdrfile2 = swig_import_helper()
    del swig_import_helper
else:
    import _libxdrfile2
del version_info
try:
    _swig_property = property
except NameError:
    pass # Python < 2.2 doesn't have 'property'.
def _swig_setattr_nondynamic(self,class_type,name,value,static=1):
    if (name == "thisown"): return self.this.own(value)
    if (name == "this"):
        if type(value).__name__ == 'SwigPyObject':
            self.__dict__[name] = value
            return
    method = class_type.__swig_setmethods__.get(name,None)
    if method: return method(self,value)
    if (not static):
        self.__dict__[name] = value
    else:
        raise AttributeError("You cannot add attributes to %s" % self)

def _swig_setattr(self,class_type,name,value):
    return _swig_setattr_nondynamic(self,class_type,name,value,0)

def _swig_getattr(self,class_type,name):
    if (name == "thisown"): return self.this.own()
    method = class_type.__swig_getmethods__.get(name,None)
    if method: return method(self)
    raise AttributeError(name)

def _swig_repr(self):
    try: strthis = "proxy of " + self.this.__repr__()
    except: strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)

try:
    _object = object
    _newclass = 1
except AttributeError:
    class _object : pass
    _newclass = 0


exdrOK = _libxdrfile2.exdrOK
exdrHEADER = _libxdrfile2.exdrHEADER
exdrSTRING = _libxdrfile2.exdrSTRING
exdrDOUBLE = _libxdrfile2.exdrDOUBLE
exdrINT = _libxdrfile2.exdrINT
exdrFLOAT = _libxdrfile2.exdrFLOAT
exdrUINT = _libxdrfile2.exdrUINT
exdr3DX = _libxdrfile2.exdr3DX
exdrCLOSE = _libxdrfile2.exdrCLOSE
exdrMAGIC = _libxdrfile2.exdrMAGIC
exdrNOMEM = _libxdrfile2.exdrNOMEM
exdrENDOFFILE = _libxdrfile2.exdrENDOFFILE
exdrFILENOTFOUND = _libxdrfile2.exdrFILENOTFOUND
exdrNR = _libxdrfile2.exdrNR
SEEK_SET = _libxdrfile2.SEEK_SET
SEEK_CUR = _libxdrfile2.SEEK_CUR
SEEK_END = _libxdrfile2.SEEK_END

def xdrfile_open(*args):
  """xdrfile_open(path, mode) -> XDRFILE *"""
  return _libxdrfile2.xdrfile_open(*args)

def xdrfile_close(*args):
  """xdrfile_close(fp) -> int"""
  return _libxdrfile2.xdrfile_close(*args)

def read_xtc_natoms(*args):
  """read_xtc_natoms(fn) -> int"""
  return _libxdrfile2.read_xtc_natoms(*args)

def read_xtc_numframes(*args):
  """read_xtc_numframes(fn) -> PyObject *"""
  return _libxdrfile2.read_xtc_numframes(*args)

def read_trr_natoms(*args):
  """read_trr_natoms(fn) -> int"""
  return _libxdrfile2.read_trr_natoms(*args)

def read_trr_numframes(*args):
  """read_trr_numframes(fn) -> PyObject *"""
  return _libxdrfile2.read_trr_numframes(*args)
DIM = _libxdrfile2.DIM

def read_xtc(*args):
  """read_xtc(XDRFILE, box, x) -> (status, step, time, precision)"""
  return _libxdrfile2.read_xtc(*args)

def read_trr(*args):
  """read_trr(XDRFILE, box, x, v, f) -> (status, step, time, lambda)"""
  return _libxdrfile2.read_trr(*args)

def write_xtc(*args):
  """write_xtc(XDRFILE, step, time, box, x, prec) -> status"""
  return _libxdrfile2.write_xtc(*args)

def write_trr(*args):
  """write_trr(XDRFILE, step, time, lambda, box, x, v, f) -> status"""
  return _libxdrfile2.write_trr(*args)

def xdr_seek(*args):
  """xdr_seek(xd, pos, whence) -> int"""
  return _libxdrfile2.xdr_seek(*args)

def xdr_tell(*args):
  """xdr_tell(xd) -> long long"""
  return _libxdrfile2.xdr_tell(*args)
# This file is compatible with both classic and new-style classes.


