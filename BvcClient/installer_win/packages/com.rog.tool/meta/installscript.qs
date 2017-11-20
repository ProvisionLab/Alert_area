function Component()
{
    // default constructor
}

Component.prototype.createOperations = function()
{
    component.createOperations();

    if (systemInfo.productType === "windows") 
    {
        component.addOperation("CreateShortcut", "@TargetDir@\\RogTool.exe", "@StartMenuDir@\\ROG Tool.lnk", 
            "workingDirectory=@TargetDir@", "iconPath=@TargetDir@\\rog.ico", "iconId=0", "description=ROG Tool");

        component.addOperation("CreateShortcut", "@TargetDir@\\RogTool.exe", "@DesktopDir@\\ROG Tool.lnk", 
            "workingDirectory=@TargetDir@", "iconPath=@TargetDir@\\rog.ico", "iconId=0", "description=ROG Tool");

        // 1638 - other version is installed
        // 3010 - reboot required
        component.addElevatedOperation("Execute", "{0,1602,1638,3010}", "@TargetDir@\\vcredist_x64.exe");
    }

    if (installer.value("os") === "x11")
    {
        component.addOperation("CreateDesktopEntry", "/usr/share/applications/ROG_Tool.desktop", 
            "Version=1.0\nType=Application\nTerminal=false\nExec=@TargetDir@/ROGTool.sh\nName=ROG Tool\nIcon=@TargetDir@rog.png\nName[en_US]=ROG Tool");
        component.addElevatedOperation("Copy", "/usr/share/applications/ROG_Tool.desktop", "@HomeDir@/Desktop/ROG_Tool.desktop");
    }
}
