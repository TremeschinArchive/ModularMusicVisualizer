import mmv

for Platform in ["Linux", "Windows"]:
    MMV = mmv.mmvPackageInterface(ForcePlatform=Platform)
    for External in (MMV.Externals.AvailableExternals.ListOfAll):
        MMV.Externals.DownloadInstallExternal(TargetExternals=External, _ForceNotFound=True)
    