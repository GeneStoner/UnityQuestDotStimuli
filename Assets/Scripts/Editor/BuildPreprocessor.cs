// Editor-only: stamps BuildInfo.BUILD_DATE with the current time before every build.
using System;
using System.IO;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;

public class BuildPreprocessor : IPreprocessBuildWithReport
{
    public int callbackOrder => 0;

    public void OnPreprocessBuild(BuildReport report)
    {
        string dateStamp = DateTime.Now.ToString("yyyy-MM-dd HH:mm");
        string content =
            "// Auto-updated by BuildPreprocessor.cs before each build.\n" +
            "// Do not edit by hand.\n" +
            "public static class BuildInfo\n" +
            "{\n" +
            $"    public const string BUILD_DATE = \"{dateStamp}\";\n" +
            "}\n";

        string path = Path.Combine(
            UnityEngine.Application.dataPath, "Scripts", "BuildInfo.cs");
        File.WriteAllText(path, content);
        AssetDatabase.ImportAsset(
            "Assets/Scripts/BuildInfo.cs",
            ImportAssetOptions.ForceUpdate);

        UnityEngine.Debug.Log($"[BuildPreprocessor] BUILD_DATE set to {dateStamp}");
    }
}
