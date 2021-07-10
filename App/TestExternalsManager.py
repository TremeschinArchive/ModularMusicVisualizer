import MMV

for Platform in ["Linux", "Windows"]:
    MMV = MMV.mmvPackageInterface(ForcePlatform=Platform)
    for External in (MMV.Externals.AvailableExternals.ListOfAll):
        MMV.Externals.DownloadInstallExternal(TargetExternals=External, _ForceNotFound=True)
    