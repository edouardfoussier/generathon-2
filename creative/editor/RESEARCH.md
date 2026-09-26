# Browser editing options — 26 September 2026

The team needs to select the strongest moments from three existing, synchronized 76-second cuts. A focused comparison editor with native FFmpeg export is the shortest route to that result. No third-party editor code was copied and no packages were installed for this implementation.

| Project | Current license and status | Implication for this project |
| --- | --- | --- |
| [OpenCut](https://github.com/OpenCut-app/OpenCut) / [Classic](https://github.com/OpenCut-app/opencut-classic) | MIT. The main repository is being rewritten; its README recommends Classic for current use. Classic is archived and no longer maintained. | Useful UI reference, but adopting its full application or its changing architecture adds work during the hackathon. |
| [Revideo](https://github.com/midrender/revideo) | [MIT license](https://github.com/midrender/revideo/blob/main/LICENSE). TypeScript scene rendering, headless renderer and React player. | An engine for creating videos with code, rather than a ready-made selection editor. A reasonable option if future work requires richer motion graphics. |
| [OpenVideo / react-video-editor](https://github.com/openvideodev/react-video-editor) | [Custom two-tier license](https://github.com/openvideodev/react-video-editor/blob/main/LICENSE), free for individuals, nonprofits and organizations with up to three employees; a company license is required outside those conditions. | Closest prebuilt UI: multitrack timeline, trim/split and client-side MP4 export through WebCodecs. It brings a Next.js application and its own rendering stack. Its current version must not be described as MIT. |
| [Remotion](https://github.com/remotion-dev/remotion) | [Custom license](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md), with free use for individuals and qualifying small organizations, plus company licensing. | React composition, player and rendering APIs are powerful for a larger product; not necessary for cutting between three existing clips. |

Repository contents and license files were checked on the date above. These are implementation tradeoffs, not a prediction of future project stability.

## Architecture selected

- Three video previews use one shared playhead; selecting a take changes the final-cut recipe.
- Existing scene boundaries seed the project, with Veo selected initially following the team's preference.
- The recipe uses integer frames at 24 fps and half-open source intervals: `inFrame` is included; `outFrame` is excluded. Output timing is the cumulative duration of the ordered segments.
- Recipes can be saved as JSON and exchanged with teammates. Local browser storage is a convenience, not a collaborative database.
- A small local HTTP service serves approved media and validates export requests. Fixed source IDs map to known local files; imported recipes do not supply shell commands or arbitrary file paths.
- Native FFmpeg decodes, trims and re-encodes the selected intervals as H.264 video with AAC audio in an MP4 container. The final export should have exactly the sum of the selected frame counts.
- The same master soundtrack supplies audio for all model choices. When clips are shortened or reordered, trim the corresponding source-time intervals from that common audio and place them with the selected clips. Merely changing the video model does not switch soundtrack versions. A later music pass can smooth deliberate structural audio edits.

Frame-accurate export should use `trim=start_frame=…:end_frame=…`, reset each segment's timestamps with `setpts`, and concatenate normalized segments. Stream-copy seeking should not be used for arbitrary edit points because those points need not coincide with encoded keyframes. FFmpeg documents the half-open frame range and the requirement that concatenated segments start at timestamp zero: [trim](https://ffmpeg.org/ffmpeg-filters.html#trim), [concat](https://ffmpeg.org/ffmpeg-filters.html#concat).

Browser playback is an interactive preview. It is not a guarantee of exact synchronized display across three independent video elements. `requestVideoFrameCallback()` can report presented frames, but does not provide a strict synchronization guarantee: [MDN documentation](https://developer.mozilla.org/en-US/docs/Web/API/HTMLVideoElement/requestVideoFrameCallback). Verify the exported frame count and sample frames at cut boundaries.

Native FFmpeg is already available on this machine. Using it avoids adding a WebAssembly runtime and is a better fit for timely 1080p exports; ffmpeg.wasm documents slower performance than native FFmpeg and increased memory consumption for multithreaded use: [ffmpeg.wasm FAQ](https://ffmpegwasm.netlify.app/docs/faq/).

## Sharing beyond this machine

The repository and JSON recipes can be shared immediately. Public static hosting can provide the interface and previews, but cannot execute native FFmpeg. A hosted export worker, or a local helper running on each teammate's computer, would be needed for equivalent MP4 exports. Realtime multi-user editing, user accounts and uploads are separate future features.
