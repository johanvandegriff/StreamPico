# OBS Websocket Function Reference
This is an abridged version of the `obs-websocket-py` documentation, for quick reference when editing the StreamPico config.

To get the full descriptions of functions, open a python console and type:
```python
import obswebsocket, obswebsocket.requests
help(obswebsocket.requests)
```

```python
AddFilterToSource(sourceName, filterName, filterType, filterSettings)
AddSceneItem(sceneName, sourceName, setVisible) -> getItemId
Authenticate(auth)
BroadcastCustomMessage(realm, data)
CreateScene(sceneName)
CreateSource(sourceName, sourceKind, sceneName, sourceSettings=None, setVisible=None) -> getItemId
DeleteSceneItem(item, scene=None)
DisableStudioMode()
DuplicateSceneItem(item, fromScene=None, toScene=None) -> getScene, getItem
EnableStudioMode()
GetAudioActive(sourceName) -> getAudioActive
GetAudioMonitorType(sourceName) -> getMonitorType
GetAuthRequired() -> getAuthRequired, getChallenge, getSalt
GetBrowserSourceProperties(source) -> getSource, getIs_local_file, getLocal_file, getUrl, getCss, getWidth, getHeight, getFps, getShutdown
GetCurrentProfile() -> getProfileName
GetCurrentScene() -> getName, getSources
GetCurrentSceneCollection() -> getScName
GetCurrentTransition() -> getName, getDuration
GetFilenameFormatting() -> getFilenameFormatting
GetMediaDuration(sourceName) -> getMediaDuration
GetMediaSourcesList() -> getMediaSources
GetMediaState(sourceName) -> getMediaState
GetMediaTime(sourceName) -> getTimestamp
GetMute(source) -> getName, getMuted
GetOutputInfo(outputName) -> getOutputInfo
GetPreviewScene() -> getName, getSources
GetRecordingFolder() -> getRecFolder
GetRecordingStatus() -> getIsRecording, getIsRecordingPaused, getRecordTimecode, getRecordingFilename
GetReplayBufferStatus() -> getIsReplayBufferActive
GetSceneItemList(sceneName=None) -> getSceneName, getSceneItems
GetSceneItemProperties(item, scene_name=None) -> getName, getItemId, getPosition, getRotation, getScale, getCrop, getVisible, getMuted, getLocked, getBounds, getSourceWidth, getSourceHeight, getWidth, getHeight, getParentGroupName, getGroupChildren
GetSceneList() -> getCurrentScene, getScenes
GetSceneTransitionOverride(sceneName) -> getTransitionName, getTransitionDuration
GetSourceFilterInfo(sourceName, filterName) -> getEnabled, getType, getName, getSettings
GetSourceFilters(sourceName) -> getFilters
GetSourceSettings(sourceName, sourceType=None) -> getSourceName, getSourceType, getSourceSettings
GetSourceTypesList() -> getTypes
GetSourcesList() -> getSources
GetSpecialSources() -> getDesktop1, getDesktop2, getMic1, getMic2, getMic3
GetStats() -> getStats
GetStreamSettings() -> getType, getSettings
GetStreamingStatus() -> getStreaming, getRecording, getStreamTimecode, getRecTimecode, getPreviewOnly
GetStudioModeStatus() -> getStudioMode
GetSyncOffset(source) -> getName, getOffset
GetTextFreetype2Properties(source) -> getSource, getColor1, getColor2, getCustom_width, getDrop_shadow, getFont, getFrom_file, getLog_mode, getOutline, getText, getText_file, getWord_wrap
GetTextGDIPlusProperties(source) -> getSource, getAlign, getBk_color, getBk_opacity, getChatlog, getChatlog_lines, getColor, getExtents, getExtents_cx, getExtents_cy, getFile, getRead_from_file, getFont, getGradient, getGradient_color, getGradient_dir, getGradient_opacity, getOutline, getOutline_color, getOutline_size, getOutline_opacity, getText, getValign, getVertical
GetTransitionDuration() -> getTransitionDuration
GetTransitionList() -> getCurrentTransition, getTransitions
GetTransitionPosition() -> getPosition
GetTransitionSettings(transitionName) -> getTransitionSettings
GetVersion() -> getVersion, getObsWebsocketVersion, getObsStudioVersion, getAvailableRequests, getSupportedImageExportFormats
GetVideoInfo() -> getBaseWidth, getBaseHeight, getOutputWidth, getOutputHeight, getScaleType, getFps, getVideoFormat, getColorSpace, getColorRange
GetVolume(source, useDecibel=None) -> getName, getVolume, getMuted
ListOutputs() -> getOutputs
ListProfiles() -> getProfiles
ListSceneCollections() -> getSceneCollections
MoveSourceFilter(sourceName, filterName, movementType)
NextMedia(sourceName)
OpenProjector(type, monitor, geometry, name)
PauseRecording()
PlayPauseMedia(sourceName, playPause)
PreviousMedia(sourceName)
ReleaseTBar()
RemoveFilterFromSource(sourceName, filterName)
RemoveSceneTransitionOverride(sceneName)
ReorderSceneItems(items, scene=None)
ReorderSourceFilter(sourceName, filterName, newIndex)
ResetSceneItem(item, scene_name=None)
RestartMedia(sourceName)
ResumeRecording()
SaveReplayBuffer()
SaveStreamSettings()
ScrubMedia(sourceName, timeOffset)
SendCaptions(text)
SetAudioMonitorType(sourceName, monitorType)
SetBrowserSourceProperties(source, is_local_file=None, local_file=None, url=None, css=None, width=None, height=None, fps=None, shutdown=None, render=None)
SetCurrentProfile(profile_name)
SetCurrentScene(scene_name)
SetCurrentSceneCollection(sc_name)
SetCurrentTransition(transition_name)
SetFilenameFormatting(filename_formatting)
SetHeartbeat(enable)
SetMediaTime(sourceName, timestamp)
SetMute(source, mute)
SetPreviewScene(scene_name)
SetRecordingFolder(rec_folder)
SetSceneItemCrop(item, top, bottom, left, right, scene_name=None)
SetSceneItemPosition(item, x, y, scene_name=None)
SetSceneItemProperties(item, scene_name=None, position=None, rotation=None, scale=None, crop=None, visible=None, locked=None, bounds=None)
SetSceneItemRender(source, render, scene_name=None)
SetSceneItemTransform(item, x_scale, y_scale, rotation, scene_name=None)
SetSceneTransitionOverride(sceneName, transitionName, transitionDuration)
SetSourceFilterSettings(sourceName, filterName, filterSettings)
SetSourceFilterVisibility(sourceName, filterName, filterEnabled)
SetSourceName(sourceName, newName)
SetSourceSettings(sourceName, sourceSettings, sourceType=None) -> getSourceName, getSourceType, getSourceSettings
SetStreamSettings(type, settings, save)
SetSyncOffset(source, offset)
SetTBarPosition(position, release=None)
SetTextFreetype2Properties(source, color1=None, color2=None, custom_width=None, drop_shadow=None, font=None, from_file=None, log_mode=None, outline=None, text=None, text_file=None, word_wrap=None)
SetTextGDIPlusProperties(source, align=None, bk_color=None, bk_opacity=None, chatlog=None, chatlog_lines=None, color=None, extents=None, extents_cx=None, extents_cy=None, file=None, read_from_file=None, font=None, gradient=None, gradient_color=None, gradient_dir=None, gradient_opacity=None, outline=None, outline_color=None, outline_size=None, outline_opacity=None, text=None, valign=None, vertical=None, render=None)
SetTransitionDuration(duration)
SetTransitionSettings(transitionName, transitionSettings) -> getTransitionSettings
SetVolume(source, volume, useDecibel=None)
StartOutput(outputName)
StartRecording()
StartReplayBuffer()
StartStopRecording()
StartStopReplayBuffer()
StartStopStreaming()
StartStreaming(stream=None)
StopMedia(sourceName)
StopOutput(outputName, force=None)
StopRecording()
StopReplayBuffer()
StopStreaming()
TakeSourceScreenshot(sourceName=None, embedPictureFormat=None, saveToFilePath=None, fileFormat=None, compressionQuality=None, width=None, height=None) -> getSourceName, getImg, getImageFile
ToggleMute(source)
ToggleStudioMode()
TransitionToProgram(with_transition=None)
TriggerHotkeyByName(hotkeyName)
TriggerHotkeyBySequence(keyId, keyModifiers)
```
