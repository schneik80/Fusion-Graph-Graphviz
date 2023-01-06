# Author - Kevin S
# Description - Export an assembly as a graphviz graph

import os
import adsk.core
import adsk.fusion
import traceback
import re

# Performs a recursive traversal of an entire assembly structure.


def traverseAssembly(parent, occurrences, currentLevel, inputString):
    for i in range(0, occurrences.count):
        occ = occurrences.item(i)

        foo1 = occ.name
        foo2 = foo1.rsplit(" ", 1)[0]  # trim version

        parent1 = parent.rsplit(" ", 1)[0]  # trim version

        foo = '"' + parent1 + '"->"' + foo2 + '"' + " ;" + "\n"

        inputString += foo

        if occ.childOccurrences:
            inputString = traverseAssembly(
                occ.name, occ.childOccurrences, currentLevel + 1, inputString
            )
    return inputString


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)
        if not design:
            ui.messageBox("No active Fusion design", "No Design")
            return

        # Get the root component of the active design.
        rootComp = design.rootComponent

        # Create the title for the output.
        parentOcc = design.parentDocument.name

        resultString = (
            'digraph "' + parentOcc + '" {' + "\n"
        )  # Change layout engine here
        resultString += 'layout="fdp";' + "\n"
        resultString += "node[width=.75,height=.5,fontsize=9]" + "\n"
        resultString += "nodesep=.2" + "\n"
        resultString += (
            "concentrate=false" + "\n"
        )  # true draw one line, false draw lines for each occurrence
        resultString += 'mode="ipsep"' + "\n"
        resultString += "diredgeconstraints=true" + "\n"
        resultString += 'overlap="false"' + "\n"

        # Call the recursive function to traverse the assembly and build the output string.
        resultString = traverseAssembly(
            parentOcc, rootComp.occurrences.asList, 1, resultString
        )

        resultString += "}"

        msg = ""
        # Set styles of file dialog.
        folderDlg = ui.createFolderDialog()
        folderDlg.title = "Choose Folder to save graphviz Graph"

        # Show file save dialog
        dlgResult = folderDlg.showDialog()
        if dlgResult == adsk.core.DialogResults.DialogOK:
            filepath = os.path.join(folderDlg.folder, parentOcc + ".dot")
            # Write the results to the file
            with open(filepath, "w") as f:
                f.write(resultString)
            ui.messageBox("Graph saved at: " + filepath)
        else:
            return

    except:
        if ui:
            ui.messageBox("Failed:\n{}".format(traceback.format_exc()))
