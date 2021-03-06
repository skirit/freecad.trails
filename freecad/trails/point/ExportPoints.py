# /**********************************************************************
# *                                                                     *
# * Copyright (c) 2019 Hakan Seven <hakanseven12@gmail.com>             *
# *                                                                     *
# * This program is free software; you can redistribute it and/or modify*
# * it under the terms of the GNU Lesser General Public License (LGPL)  *
# * as published by the Free Software Foundation; either version 2 of   *
# * the License, or (at your option) any later version.                 *
# * for detail see the LICENCE text file.                               *
# *                                                                     *
# * This program is distributed in the hope that it will be useful,     *
# * but WITHOUT ANY WARRANTY; without even the implied warranty of      *
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the       *
# * GNU Library General Public License for more details.                *
# *                                                                     *
# * You should have received a copy of the GNU Library General Public   *
# * License along with this program; if not, write to the Free Software *
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307*
# * USA                                                                 *
# *                                                                     *
# ***********************************************************************

import FreeCAD
import FreeCADGui
from PySide import QtCore, QtGui
from freecad.trails import ICONPATH
import os

class ExportPoints:
    """
    Command to export points to point file.
    """

    def __init__(self):
        """
        Constructor
        """

        # Set icon,  menu text and tooltip
        self.Resources = {
            'Pixmap': ICONPATH + '/icons/ExportPoints.svg',
            'MenuText': "Export Points",
            'ToolTip': "Export points to point file."
        }

        # Get file path
        self.Path = os.path.dirname(__file__)

        # Get *.ui file(s)
        self.EP = FreeCADGui.PySideUic.loadUi(self.Path + "/ExportPoints.ui")

        # UI connections
        UI = self.EP
        UI.BrowseB.clicked.connect(self.FileDestination)
        UI.ExportB.clicked.connect(self.ExportPointsToFile)
        UI.CancelB.clicked.connect(UI.close)

    def GetResources(self):
        """
        Return the command resources dictionary.
        """

        return self.Resources

    def IsActive(self):
        """
        Define tool button activation situation
        """
        # Check for document
        if FreeCAD.ActiveDocument is None:
            return False
        return True

    def Activated(self):
        """
        Command activation method
        """
        # Create 'Point_Groups' group
        try:
            PointGroups = FreeCAD.ActiveDocument.Point_Groups.Group
        except Exception:
            FreeCAD.ActiveDocument.addObject(
                "App::DocumentObjectGroup", 'Point_Groups')
            PointGroups = FreeCAD.ActiveDocument.Point_Groups.Group
            PointGroups.Label = "Point Groups"

        # Set and show UI
        UI = self.EP
        UI.setParent(FreeCADGui.getMainWindow())
        UI.setWindowFlags(QtCore.Qt.Window)
        UI.show()

        # Clear previous operation
        UI.FileDestinationLE.clear()
        UI.PointGroupsLW.clear()

        # Add point groups to QListWidget
        self.GroupList = []
        for PointGroup in PointGroups:
            self.GroupList.append(PointGroup.Name)
            SubGroupName = PointGroup.Label
            UI.PointGroupsLW.addItem(SubGroupName)

    def FileDestination(self):
        """
        Get file destination.
        """
        # Select file
        UI = self.EP
        fileName = QtGui.QFileDialog.getSaveFileName(
            None, 'Save File', os.getenv("HOME"), Filter='*.txt')

        # Add ".txt" if needed
        if fileName[0][-4:] == ".txt":
            fn = fileName[0]
        else:
            fn = fileName[0] + ".txt"

        UI.FileDestinationLE.setText(fn)

    def ExportPointsToFile(self):
        """
        Export selected point group(s).
        """
        # Get user inputs
        UI = self.EP
        PointName = UI.PointNameLE.text()
        Northing = UI.NorthingLE.text()
        Easting = UI.EastingLE.text()
        Elevation = UI.ElevationLE.text()
        Description = UI.DescriptionLE.text()
        Format = ["", "", "", "", ""]
        FileDestinationLE = UI.FileDestinationLE.text()

        if FileDestinationLE.strip() == "" or UI.PointGroupsLW.count() < 1:
            return

        # Set delimiter
        if UI.DelimiterCB.currentText() == "Space":
            Delimiter = ' '
        elif UI.DelimiterCB.currentText() == "Comma":
            Delimiter = ','

        # Create point file
        try:
            File = open(FileDestinationLE, 'w')
        except Exception:
            FreeCAD.Console.PrintMessage("Can't open file")

        # Get selected point groups
        Counter = 1
        for SelectedIndex in UI.PointGroupsLW.selectedIndexes():
            Index = self.GroupList[SelectedIndex.row()]
            PointGroup = FreeCAD.ActiveDocument.getObject(Index)

            # Print points to the file
            for Point in PointGroup.Points.Points:
                pn = str(Counter)
                xx = str(round(float(Point.x) / 1000, 3))
                yy = str(round(float(Point.y) / 1000, 3))
                zz = str(round(float(Point.z) / 1000, 3))
                Format[int(PointName)-1] = pn
                Format[int(Easting)-1] = xx
                Format[int(Northing)-1] = yy
                Format[int(Elevation)-1] = zz
                Format[int(Description)-1] = ""
                Counter += 1

                File.write(Format[0]+Delimiter+Format[1]+Delimiter +
                           Format[2]+Delimiter+Format[3]+Delimiter+Format[4] +
                           "\n")
        File.close()

FreeCADGui.addCommand('Export Points', ExportPoints())
