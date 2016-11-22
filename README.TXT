This is the readme for NetLogoDoc 0.1, written by Henrik Warpefelt (henrik@warpefelt.se). 

This software was initially written for the SES-LINK project (http://www.seslink.org) at Stockholm Resilience Centre (http://www.stockholmresilience.org).

Last revised 2016-11-22. 

License
-------
NetLogoDoc uses the MIT license. Please see LICENSE.TXT for specifics. 

Usage
-----
NetLogoDoc is run by invoking it as a python script using the following syntax:
	
	python netlogodoc.py

This will cause NetLogoDoc to ask for a filename. Optionally, the user may invoke it with an argument: 

	python netlogodoc.py myfile.nls

This will cause NetLogoDoc to process the specified file. Subsequent command line arguments are ignored. NetLogoDoc accepts either pure source code (what's usually contained in a .nls file) or a .nlogo file. In the latter case, NetLogoDoc will extract the code from the file. 

When invoked with a valid file NetLogoDoc will create a subdirectory with the same name, plus the suffix "-docs". Hence, MyModule would result in the subdirectory "MyModule-docs"

Comment syntax
--------------
NetLogoDoc reads comments from the NetLogo code file and generates documentation based on what it finds. In order for NetLogoDoc to process a line, it must begin with three semicolons followed by a space (";;; "). This signalsthat NetLogoDoc should process the line and its contents.

Users may (and should) provide some additional metadata fields. Unless otherwise each field takes one argument. At the module level, these are:
	
	@author		The author of the file
	@email		The author's e-mail address
	@date		Date last revised
	@version	Version number of the module

NetLogoDoc has some limited awareness of syntax, and will process properly formatted comments inside functions al belonging to that function. Users may also specify additional metadata fields for a function. At the function level, these are: 
	
	@param		Parameter name and description. May occur more than once.
	@report		The returned value of the function. 

Examples
--------
The following code contains a commented code examples. 

Module definition for the NetLogo Turtles tutorial module: 
;;; Turtles tutorial
;;; @author Henrik Warpefelt
;;; @email henrik@warpefelt.se
;;; @version 1.0
;;; @date 2016-11-22

An example of a function that takes no arguments: 
to setup 
	;;; Sets up the simulation
	clear-all
	setup-patches
	setup-turtles 20
	reset-ticks
end

An example of a function that takes an argument:
to setup-turtles [num-turtles]
	;;; Sets up the turtles for the simulation
	;;; @param num-turtles Number of turtles to create initially
	create-turtles num-turtles
	ask turtles [ setxy random-xcor random-ycor ]
end

An example of a procedure that takes two arguments and returns a value: 
to-report sum-numbers [number1 number2]
	;;; Sums up two numbers
	;;; @param number1 The first number
	;;; @param number2 The second number
	;;; @report A sum of the first two numbers
	report number1+number2
end
