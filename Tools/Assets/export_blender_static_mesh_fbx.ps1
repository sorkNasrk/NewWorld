param(
    [Parameter(Mandatory = $true)]
    [string]$BlendPath,

    [Parameter(Mandatory = $true)]
    [string]$OutputFbx,

    [string[]]$ObjectNames = @(),

    [switch]$AllowOutsideAIWork,

    [string]$BlenderPath = "G:\blender-5.2.1-windows-x64\blender.exe"
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $projectRoot

function Resolve-ProjectPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [switch]$MustExist
    )

    $candidate = if ([System.IO.Path]::IsPathRooted($Path)) {
        $Path
    } else {
        Join-Path $projectRoot $Path
    }

    $fullPath = [System.IO.Path]::GetFullPath($candidate)
    if ($MustExist) {
        return (Resolve-Path -LiteralPath $fullPath).Path
    }
    return $fullPath
}

function ConvertTo-NormalizedPath {
    param([Parameter(Mandatory = $true)][string]$Path)
    return [System.IO.Path]::GetFullPath($Path).TrimEnd([char[]]@('\', '/')).ToLowerInvariant()
}

function Test-PathUnderRoot {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Root
    )

    $normalizedPath = ConvertTo-NormalizedPath $Path
    $normalizedRoot = ConvertTo-NormalizedPath $Root
    return $normalizedPath -eq $normalizedRoot -or $normalizedPath.StartsWith($normalizedRoot + "\")
}

if (-not (Test-Path -LiteralPath $BlenderPath)) {
    throw "Blender executable not found: $BlenderPath"
}

$blendFullPath = Resolve-ProjectPath -Path $BlendPath -MustExist
$outputFullPath = Resolve-ProjectPath -Path $OutputFbx

if ([System.IO.Path]::GetExtension($blendFullPath).ToLowerInvariant() -ne ".blend") {
    throw "BlendPath must point to a .blend file: $blendFullPath"
}

if ([System.IO.Path]::GetExtension($outputFullPath).ToLowerInvariant() -ne ".fbx") {
    throw "OutputFbx must end in .fbx: $outputFullPath"
}

$aiWorkRoot = Resolve-ProjectPath -Path "Content\NewWorld\AIWork" -MustExist
if (-not $AllowOutsideAIWork -and -not (Test-PathUnderRoot -Path $outputFullPath -Root $aiWorkRoot)) {
    throw "OutputFbx must stay under Content\NewWorld\AIWork unless -AllowOutsideAIWork is set: $outputFullPath"
}

$outputDirectory = Split-Path -Parent $outputFullPath
if (-not (Test-Path -LiteralPath $outputDirectory)) {
    New-Item -ItemType Directory -Force -Path $outputDirectory | Out-Null
}

$normalizedObjectNames = @(
    $ObjectNames |
        ForEach-Object { [string]$_ -split "," } |
        ForEach-Object { $_.Trim() } |
        Where-Object { $_ }
)
$objectNameJson = ConvertTo-Json -InputObject @($normalizedObjectNames) -Compress
$pythonScript = @'
import bpy
import json
import os
import sys

def main():
    output_fbx = os.environ["NEWWORLD_OUTPUT_FBX"]
    object_names = json.loads(os.environ.get("NEWWORLD_EXPORT_OBJECTS", "[]"))

    if object_names:
        objects = []
        missing = []
        not_mesh = []
        for name in object_names:
            obj = bpy.data.objects.get(name)
            if obj is None:
                missing.append(name)
                continue
            if obj.type != "MESH":
                not_mesh.append(f"{name}:{obj.type}")
                continue
            objects.append(obj)
        if missing:
            raise RuntimeError("Missing requested Blender objects: " + ", ".join(missing))
        if not_mesh:
            raise RuntimeError("Requested objects must be MESH: " + ", ".join(not_mesh))
    else:
        objects = [
            obj for obj in bpy.context.scene.objects
            if obj.type == "MESH"
            and not obj.hide_get()
            and not obj.name.startswith("REF_")
            and "ReferencePlane" not in obj.name
        ]

    objects = sorted(objects, key=lambda obj: obj.name)
    if not objects:
        raise RuntimeError("No mesh objects were selected for FBX export.")

    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]

    os.makedirs(os.path.dirname(output_fbx), exist_ok=True)

    bpy.ops.export_scene.fbx(
        filepath=output_fbx,
        use_selection=True,
        object_types={"MESH"},
        global_scale=100.0,
        axis_forward="-Z",
        axis_up="Y",
        apply_unit_scale=True,
        apply_scale_options="FBX_SCALE_UNITS",
        bake_space_transform=False,
        use_mesh_modifiers=True,
        mesh_smooth_type="FACE",
        use_tspace=True,
        path_mode="AUTO",
    )

    summary = {
        "blend_path": bpy.data.filepath,
        "output_fbx": output_fbx,
        "object_count": len(objects),
        "objects": [
            {
                "name": obj.name,
                "type": obj.type,
                "vertices": len(obj.data.vertices),
                "polygons": len(obj.data.polygons),
                "dimensions": [round(v, 6) for v in obj.dimensions],
                "location": [round(v, 6) for v in obj.location],
                "scale": [round(v, 6) for v in obj.scale],
                "material_slots": [slot.name for slot in obj.material_slots],
            }
            for obj in objects
        ],
    }

    print("NEWWORLD_FBX_EXPORT_SUMMARY " + json.dumps(summary, sort_keys=True))

try:
    main()
except Exception as exc:
    print("NEWWORLD_FBX_EXPORT_ERROR " + repr(exc))
    sys.exit(2)
'@

$tempScriptPath = Join-Path ([System.IO.Path]::GetTempPath()) ("newworld_blender_fbx_export_{0}.py" -f ([System.Guid]::NewGuid().ToString("N")))
$oldOutputEnv = $env:NEWWORLD_OUTPUT_FBX
$oldObjectsEnv = $env:NEWWORLD_EXPORT_OBJECTS

try {
    Set-Content -LiteralPath $tempScriptPath -Value $pythonScript -Encoding UTF8
    $env:NEWWORLD_OUTPUT_FBX = $outputFullPath
    $env:NEWWORLD_EXPORT_OBJECTS = $objectNameJson

    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $blenderOutput = & $BlenderPath --background $blendFullPath --python $tempScriptPath 2>&1
        $exitCode = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    $blenderLines = @($blenderOutput | ForEach-Object { $_.ToString() })
    if ($exitCode -ne 0) {
        $message = ($blenderLines | Out-String).Trim()
        $newline = [Environment]::NewLine
        throw "Blender FBX export failed with exit code $exitCode.$newline$message"
    }

    if (-not (Test-Path -LiteralPath $outputFullPath)) {
        throw "Blender reported success but the FBX was not created: $outputFullPath"
    }

    $summaryLine = @($blenderLines | Where-Object { $_ -like "NEWWORLD_FBX_EXPORT_SUMMARY *" } | Select-Object -Last 1)
    if (-not $summaryLine) {
        $recentOutput = ($blenderLines | Select-Object -Last 20 | Out-String).Trim()
        $newline = [Environment]::NewLine
        throw "Blender export completed but did not return a NewWorld summary line.$newline$recentOutput"
    }

    $summaryJson = $summaryLine.Substring("NEWWORLD_FBX_EXPORT_SUMMARY ".Length)
    $summary = $summaryJson | ConvertFrom-Json
    $summary | Add-Member -NotePropertyName "output_size_bytes" -NotePropertyValue ((Get-Item -LiteralPath $outputFullPath).Length)
    $summary | ConvertTo-Json -Depth 20
} finally {
    if ($null -eq $oldOutputEnv) {
        Remove-Item Env:\NEWWORLD_OUTPUT_FBX -ErrorAction SilentlyContinue
    } else {
        $env:NEWWORLD_OUTPUT_FBX = $oldOutputEnv
    }

    if ($null -eq $oldObjectsEnv) {
        Remove-Item Env:\NEWWORLD_EXPORT_OBJECTS -ErrorAction SilentlyContinue
    } else {
        $env:NEWWORLD_EXPORT_OBJECTS = $oldObjectsEnv
    }

    Remove-Item -LiteralPath $tempScriptPath -Force -ErrorAction SilentlyContinue
}
