# mmLib-2.0.x: Python Macromolecular Library (mmLib)
URL of original project: http://pymmlib.sourceforge.net/

Ported to Python3

## REVISIONS:
  * 2024-11-09: 2.0.5: Runs using Python3
  * 2024-11-06: 2.0.0: Runs using Python3
  * 2011-03-27: 1.2.0: Skittles/validation support
  * 2008-02-26: 1.1.0: PHENIX support; Christoph Champ
  * 2007-04-28: 1.0.0

## DESCRIPTION:
The Python Macromolecular Library (mmLib) is a collection of Python 
modules the examination and manipulation of macromolecular structures,
and the files which describe them.

## REQUIREMENTS:
  * Python >= 3.8
  * numpy  >= 1.26

GUI and OpenGL not tested under Python3

Additional requirements for the mmCIF Editor and tlsview.py Viewer:
  * PyOpenGL   >= 2.0.0.44 (http://pyopengl.sourceforge.net/)
  * gtk        >= 2.0/2.2  (http://www.gtk.org/)
  * PyGtk      >= 1.99.16  (http://www.pygtk.org/)
  * GtkGLExt   >= 1.0      (http://gtkglext.sourceforge.net)
  * PyGtkGLExt >= 1.0      (http://gtkglext.sourceforge.net)

HARDWARE:
If you want to use the GLViewer.py module, or use the mmLib Molecular 
Viewer, you will need OpenGL hardware acceleration provided by your video
card and driver. We have tested this on a NVIDIA 5200FX using RedHat 9.0
and the latest NVIDIA-6106 driver.

# INSTALLATION:
`pip install pymmlib3`
More here but this document is mostly outdated: INSTALL.txt

## PROBLEMS/BUG REPORTS/CONTACT:
You can contact us through our SourceForge site, or email us directly at:
  * Ethan Merritt <merritt@u.washington.edu>
  * Christoph Champ <champc@u.washington.edu>
  * Jay Painter <jpaint@u.washington.edu>
  * Pawel Rubach <pawel.rubach@gmail.com>
