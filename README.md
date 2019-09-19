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

    3)  Steady state simulation
    
    4)  Charts of simulation results
    
    5)  ASM 1, 2d, and 3

    6)  User defined models

    7)  User defined unit processes

1.2 RUNNING ENVIRONMENT:

    1)  Python 3
    
    2)  Matplotlib
    
    3)  PyQT4 or wxWidgets (I haven't decided)

    4)  SciPy/NumPy/Pandas (Possible, if needed down the road)
    
1.3 LICENSES:

    Please refer to the attached License.txt document for details.


1.4 OBJECTIVES OF THIS GENERAL DEVELOPMENT PLAN
    
    This Development Plan ("the Plan") is to provide general guidelines for 
    developers on the key fuctionalities, structure, and coordination
    aspects of the project. It is not meant to provide detail instructions
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
        The current strategy for running steady state simulation is to
        integrate the differential equation system using the Euler's method for
        each process unit, with constant influent conditions (or the average of
        the variable flows and loads), the results of the current iteration
        will be compared to the previous. If the two sets of results are close
        to each other within the preset convergence criteria for all the units,
        the current results are considered the steady state. If not, the
        current results will be used for the downstream unit's input until
        the maximum number of allowed iteration is reached.

        Pseudo-Code for Steady State:
            IF ALL THE UNITS IN THE WWTP ARE NOT CONVERGED AND NUMBER OF
                ITERATION IS LESS THAN THE MAXIMUM:
                FROM THE INFLUENT OF THE WWTP:
                    LOOP:
                    GO TO THE NEXT UNIT ON THE PFD
                    INTEGRATE MODEL COMPONENTS --> UNIT_C_CURRENT[]
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
                Good initial guess is important for the success of the
                integration.

                Current initial guess strategy follows the suggestion on the
                IWA ASM 1 report. 

    3.3 Dynamic Simulation
        The approach for the dynamic simulation is expected to take a different
        approach (Plant Wide Differential Equation System) than that of the
        steady state (Sequential Modular Approach).

        From a project management standpoint, it is easier to use the
        same approach (equation system) for both steady state and dynamic
        simulations. There are papers in the 1980's comparing the pros and cons
        of the two approaches. The reason for having them both in PooPyLab is
        Kai's own learning purpose.

        The equation system solver will be something like RK4. And there
        will be a time period defined by the user for the length of the
        simulation. Influent concentrations at a particular time may need to be
        interpolated based on user input.
        
        Much thinking still need to be put into the dyanmic simulation.

        3.3.1   Initial Guess
                For dynamic simulation, the initial guess will be the steady 
                state solution.

    3.4 Model Modification and Extension by Users
        Not much plan has been developed for this PooPyLab functionality at 
        this point. It could make the software much more complicated if we
        want to provide a GUI for it. 
        
        However, since PooPyLab is open source, it may be easier for users to 
        simply use the source code to inherite, modify, and extend the models 
        directly. The users can save the revised models in a separate folder of 
        the PooPyLab project and share with others. That being said, it is 
        probably still desirable to have extension functionality via the GUI
        that allows user to define his/her own equation systems (another reason
        to use equation system for both steady state and dynamic simulations).

        Current plant is to specify all models in .csv format once ASM 1
        testing is finished. It will allow a user to define his/her own models
        with grid view in a spreadsheet program or text files (not as easy to
        read or revise).
        
        ANY INPUT ON THIS TOPIC IS WELCOME!

    3.5 Report Simulation Results
        The results of either steady state or dynamic simulations will need to
        be presented in tables and/or plots. 

        Available packages like openPyXL can be used to pipe the output to an
        Excel spreadsheet.

        Alternatively, .csv files can be used to store the results.

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
        repository on github.com to see their most recent status and any
        additional files.
        
        4.3.1   Base (poopy_lab_obj): Common abstract interfaces only.
        4.3.2   Splitter (stream.splitter): Multiple inlet, one main outlet and
                one side outlet;
        4.3.3   Pipe (stream.pipe): A Splitter without side outlet;
        4.3.4   Influent (stream.influent): A Pipe that has no further upstream;
        4.3.5   Effluent (stream.effluent): A Pipe that has no further downstream;
        4.3.6   WAS (stream.was): Waste Activated Sludge unit that is a Pipe and that
                is able to determine waste sludge flow according to the sludge
                retention time;
        4.3.7   ASMReactor (bio.asm_reactor): A Pipe that has active volume and can
                react
        4.3.8   Final_Clarifier (phys_chem/final_clarifier): A Splitter that has
                different solids concentrations at its main and side outlets;
        4.3.9   ASM1 (ASMModel.asm1): ASM 1 model kinetics and stoichiometrics
        4.3.10  pyASM1v0_6.py: "analytical" approach to generate initial guess
        4.3.11  test/: Folder for testing the defined classes
        4.3.12  Process Flow Diagram Utilities (utils.pfd): global functions
                that check validity of connections and unit processes
        4.3.13  Main Loop Run Utilities (utils.run): global functions for top
                level main loop running the simulation for the entire PFD.

    4.4 Testing Done:
        4.4.1   Connectivity
        4.4.2   Inlet receiving and outlet discharge
        4.4.3   ASM1 integration
        4.4.4   PFD validation
    
===============================================================================

5.0 TO DO LIST
    This section shall be constantly edited by Kai Zhang to reflect the current
    need for the development.

    5.1 ADDITIONAL THOUGHTS SHALL BE PUT IN TO EVALUATE WHETHER THE EQUATION
        BASED APPROACH OFFERS ANY SPECIFIC ADVANTAGES OVER THE CURRENT ONE.

    5.2 CONTINUE TO TEST THE INTERACTION OF THE PROCESS UNITS, ESPECIALLY
        5.2.1   SLUDGE WASTING AND SRT CONTROL.
        5.2.2   FINAL CLARIFIER FUNCTIONS
    
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

LAST UPDATE: 2019-09-18 KZ
