Leap Motion Mouse Controller
==========
Leap controlled Mac OSX mouse 


Install
====

PyMouse for moving and clicking mouse. 
`sudo easy_install pymouse`


Also need access to `Leap.py` Python module in `LeapDeveloperKit/LeapSDK/lib/` to Python's path.

What I did was create symbolic link to the LeapSDK folder to some target file in my project directory.


To create a symbolic link, enter:

`$ ln -s {/path/to/LeapDeveloperKit/LeapSDK} {link-name}`

Example, `cd` to the location of your project then enter this command

`$ ln -s /usr/local/LeapDeveloperKit/LeapSDK/ lib/`

