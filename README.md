GENERAL DEVELOPMENT PLAN FOR POOPYLAB
*******************************************************************************

1.0 INTRODUCTION:

    PooPyLab is a biological wastewater treatment software that is built upon 
    Activated Sludge Models (ASM 1,2d, & 3) developed by the International 
    Water Association (IWA).

    There are commercial softwares like BioWin, GPS-X, and others that provide
    similar core functionalities for wastewater engineers and students. However,
    their model implementations may be proprietary and hidden from the users. 
    PooPyLab is a free open source software that offers a platform for ASM model
    related research and integrating computer programming with environmental
    science/engineering.
  
1.1 BASIC FEATURES:

    1)  GUI for wastewater treatment plant process setup
    
    2)  Treatment units include:
        a)  Single Completely Mixed Stirred Tank (CSTR) reactor (For Plug Flow 
            Reactor, or PFR, please use CSTR-in-series to mimick)
        b)  Influent Unit
        c)  Effluent Unit
        d)  Flow Splitter
        e)  Waste Activated Sludge (WAS) Unit
        f)  Facility Life Cycle Assessment (LCA)

    3)  Steady state simulation
    
    4)  Charts of simulation results
    
    5)  ASM 1, 2d, and 3

1.2 RUNNING ENVIRONMENT:

    1)  Python 3
    
    2)  SciPy & NumPy
    
    3)  Matplotlib
    
    4)  PyQT4
    
    5)  Linux (Windows and Mac environments to be tested)

1.3 LICENSES:

    Please refer to the attached License.txt document for details.


1.4 OBJECTIVES OF THIS GENERAL DEVELOPMENT PLAN
    
    This Development Plan ("the Plan") is to provide general guidelines for 
    developers on the key fuctionalities, structure, and coordination
    aspect of the project. It is not meant to provide detail instructions
    on how to write the codes. Ideally, the whole PooPyLab package will
    be subdivided into smaller sections that provide their own functionalities
    and work with each other to complete the main objectives of the software.
    For example, the Plan will define the core process units that are commonly
    used in wastewater treatment plants (WWTP) that utilized activated sludge.
    These may include biological reactors, clarifiers, waste activated sludge
    (i.e. WAS) handling, etc. The Plan specifies the input, output, and
    treatment process of each unit. The developer can then code to provide
    the interface for these units to enable them take input, do steady state
    and/or dynamic simulations, output results, communicate with up- and
    downstream process units, and report errors.

    The Plan provide the following basic information for the development team:

    1)  Structure of the software;
    
    2)  Core functionalities;

    3)  Classes and procedures needed to accomplish the core functionalities;

    4)  Summary of what had been under development (note: this will be a 
        continuous update as the project moves forward);

    5)  Summary of what still needs to be added (note: this will be a continous
        update as the project moves forward);

    6)  General guidelines for schedule/milestones/releases.

===============================================================================

2.0 STRUCTURE OF THE SOFTWARE
    Please refer to the attached structure diagram (COMING SOON)

===============================================================================

3.0 FUNCTIONALITIES

    3.1 Graphic User Interface (GUI):
        3.1.1   "Drag and Drop" to setup Process Flow Diagram (PFD):
            3.1.1.1 Automatic addition/removal of process units in the program
                    to match the PFD;
            3.1.1.2 Storage of the PFD in a file that can be used to re-create
                    the diagram;
            3.1.1.3 Re-create the PFD and project conditions from saved files.
        3.1.2   Automatic recongnition of flow directions for Pipes
        3.1.3   Edition of process unit's properties by double-clicking on the
                units, such as reactor volumes, dimensions, dissoved oxygen,
                local model parameters, etc.
        2.1.4   Validity check of the PFD.

    3.2 Steady State Simulation
        The current strategy for running steady state simulation is to solve
        the mass balance equations in each process unit, the results of the 
        current iteration will be compared to the previous. If the two set of 
        results are close to each other within the preset convergence
        criteria for all the units, the current results are considered the
        steady state. If not, the current results will be used for the down-
        stream unit's input until the maximum number of allowed iteration is
        reached.

        Pseudo-Code:
            IF ALL THE UNITS IN THE WWTP ARE NOT CONVERGED AND NUMBER OF
                ITERATION IS LESS THAN THE MAXIMUM:
                FROM THE INFLUENT OF THE WWTP:
                    LOOP:
                    GO TO THE NEXT UNIT ON THE PFD
                    SOLVE MODEL COMPONENTS FOR THIS UNIT --> UNIT_C_CURRENT[]
                    IF MAX(ABS(UNIT_C_CURRENT[] - UNIT_C_PREVIOUS[])) 
                        <= CONVERGE_CRITERIA
                        MARK UNIT AS CONVERGED
                    ELSE
                        MARK UNIT AS NOT CONVERGED
                        UNIT_C_PREVIOUS[] = UNIT_C_CURRENT[]
                    LOOP CONTINUES UNTIL ALL THE UNITS HAVE BEEN CHECKED IN 
                        THIS ROUND
            ELSE:
                OUTPUT CONVERGED RESULTS
                TERMINTATE THE ITERATION

        3.2.1   Initial Guess
                The solver for the steady state simulation is Newton-Raphson
                (or one of its variations), which requires initial guess to
                begin. Good initial guess is a key for the success of the 
                solver runs. 

                Currently, PooPyLab is using ASM1 which doesn't deal with 
                biological phosphorus (P) removal. Therefore, the initial 
                guess on the first reactor (either an anoxic or aerobic) is 
                relatively simple. When it comes to ASM2 and/or ASM3 where BPR 
                and/or cellular storage are a part of the model, initial guess 
                will need to be revisited and carefully developed.

    3.3 Dynamic Simulation
        The approach for the dynamic simulation is expected to be similar to 
        that of the steady state (Sequential Modular Approach), except that the 
        solver will be something like RK4. And there will be a time period 
        defined by the user for the length of the simulation. Influent 
        concentrations at a particular time may need to be interpolated based 
        on user input. 
        
        Much thinking still need to be put into the dyanmic simulation.

        Another approach for the dynamic simulation is to generate the entire
        group of equations for the overall PFD, and then solve simultaneously
        for the time (Equation Based Approach). There are papers in the 1980's
        comparing the pros and cons of the two approaches. I (Kai) personally
        think that the Sequential Modular Approach may fit the object oriented
        programming scheme better, since we are programming in Python, an OOP
        language.

        3.3.1   Initial Guess
                For dynamic simulation, the initial guess will be the steady 
                state solution.

    3.4 Model Modification and Extension
        Not much plan has been developed for this PooPyLab functionality at 
        this point. It could make the software much more complicated if we
        want to provide a GUI for it. 
        
        However, since PooPyLab is open source, it may be easier for users to 
        simply use the source code to inherite, modify, and extend the models 
        directly. The users can save the revised models in a separate folder of 
        the PooPyLab project and share with others. That being said, it is 
        probably still desirable to have extension functionality via the GUI. 
        If that is to be implemented, there could be the need for code writing
        code. 
        
        ANY INPUT ON THIS TOPIC IS WELCOME!

    3.5 Report Simulation Results
        The results of either steady state or dynamic simulations will need to
        be presented in tables and/or plots.

    3.6 Storage and Reloading of Simulation Results
        PooPyLab shall be able to store the simulation results, reload the 
        previous results when the user open his/her saved project.

    3.7 ANY OTHER SUGGESTIONS AND IDEAS??

===============================================================================

4.0 CURRENT STATUS (WHAT HAVE BEEN DONE)
    This section shall be constantly edited by Kai Zhang to reflect the most 
    recent status of the development.

    4.1 Classes
        Please refer to the attached UML diagram and the source code for the 
        definitions of the key classes, and their relationship to each other.

        Please note that the UML diagram may lack behind the code development.
        If there are any discrepency between the UML and the source code, 
        please use the source code as the accurate/correct information and 
        inform the development team about the discrepency.

    4.2 Definition of ASM1
        The representation of the ASM models will be in the file asm.py. 
        Currently only ASM1 has been added.

    4.3 Definitions of Classes
        The following classes have been in place with initial definitions.
        However, they are revised constantly. Please refer to the project's
        repository on GITHUB to see their most recent status and any additional
        files.
        
        4.3.1   Base: Common abstract interfaces only.
        4.3.2   Pipe: Basic flow functions. Multiple inlets, single outlet.
        4.3.3   Reactor: A Pipe that has active volume and can react.
        4.3.4   Influent: A unique unit without any upstreams (inlets).
        4.3.5   Effluent: A unique unit without any downstream (outlet).
        4.3.6   Branch: Similar to Influent, but to be used as part of a 
                    Splitter.
        4.3.7   Splitter: Combination of Pipe and Branch.
        4.3.8   Clarifier: Currently behave like a Splitter without settling
                    model built in.
        4.3.9   WAS: Waste sludge leaves the WWTP from here. Acts like an 
                    Effluent, but with the capability of SRT control.
        4.3.10  pyASM1v0_6.py: Preliminary test of the ASM1 and 
                    scipy.integrate.fsolve() on a CSTR reactor using an example
                    from Grady Jr. (1999): Biological Wastewater Treatment,
                    2nd Edition.
        4.3.11  MainTest.py: Testing the connections among different process
                    units with the current class definitions.
    
===============================================================================

5.0 TO DO LIST
    This section shall be constantly edited by Kai Zhang to reflect the current
    need for the development.

    5.1 THE CURRENT PLAN FOR BOTH STEADY STATE AND DYANMIC SIMULATIONS IS TO 
        USE THE SEQUENTIAL MODULAR APPROACH. ADDITIONAL THOUGHTS SHALL BE PUT
        IN TO EVALUATE WHETHER THE EQUATION BASED APPROACH OFFERS ANY SPECIFIC
        ADVANTAGES OVER THE CURRENT ONE.

    5.2 CONTINUE TO TEST THE INTERACTION OF THE PROCESS UNITS, ESPECIALLY
        5.2.1   SLUDGE WASTING AND SRT CONTROL.
        5.2.2   RECEIVING, BLENDING, AND TRANSFERRING FLOW AND MODEL COMPONENTS
                FROM UPSTREAM UNITS TO DOWNSTREAM ONE.
        5.2.3   SIDESTREAM INTERACTION WITH OTHER UNITS.
    
    5.3 DEVELOP A CLASS FOR EXTERNAL CARBON ADDITION UNIT.

    5.4 DEVELOP TESTING CASES FOR ASM1 STEADY STATE SIMULATION
        5.4.1   SINGLE CSTR FOR ORGANIC AND AMMONIA OXIDATION.
        5.4.2   CSTR IN SERIES FOR ORGANIC AND AMMONIA OXIDATION.
        5.4.3   MLE WITH SINGLE CSTR PRE-ANOXIC AND AERATION ZONES.
        5.4.4   MLE WITH CSTR-IN-SERIES PRE-ANOXIC AND AERATION ZONES.
        5.4.5   PRE-ANOXIC, AEROBIC, FOLLOWED BY POST-ANOXIC. EXTERNAL CARBON
                ADDITION.

    5.5 ADD CAPABILITY OF STORING AND READING PROCESS FLOW DIAGRAM AND MODEL
        SETTINGS.

    5.6 DEVELOP GRAPHIC USER INTERFACE (GUI)
        5.6.1   ICONS FOR EACH UNIT TYPE.
        5.6.2   DRAG AND DROP CAPABILITY.
        5.6.3   CONNECT PROCESS FLOW DIAGRAM TO CODE

