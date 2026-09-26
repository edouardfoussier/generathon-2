# Méthode Higgsfield appliquée à Converse / Applied workflow

26 September 2026 · Working notes for animatic v1

## Avis / Assessment

**FR.** Le guide est utile pour structurer la fabrication : personnages cohérents, décors réutilisables, images clés, puis animation plan par plan. Sa promesse de publicité « $350,000 » est un titre promotionnel, pas une mesure de qualité que nous pouvons reprendre à notre compte. Pour notre film intime, la précision d'un regard, la lisibilité de la chaussure et un raccord juste comptent davantage que les effets spectaculaires.

**EN.** The guide provides a useful production structure: consistent characters, reusable locations, keyframes, then shot-specific animation. Its “$350,000” headline is promotional, not a quality benchmark for our film. Here, a readable look, a recognizable shoe and a motivated cut matter more than spectacle.

Sources: [Higgsfield commercial guide](https://higgsfield.ai/blog/ai-commercial-youtube-guide), [official skills repository](https://github.com/higgsfield-ai/skills).

## Ce que nous appliquons / What we apply

| Practice | Application to this film |
|---|---|
| Reference first | Luna T01/X01/L01; Rafa G01 and the approved-age keyframes; attic D06. Elena and Mom use the newly proposed family sheets. |
| Separate identity, place and action | New close-ups retain the cast and wardrobe from their scene masters before any motion is requested. |
| One action per generated clip | A glance, a weight shift, a hand offered, a lace tightened. Short motion prompts avoid repeating the entire still-image description. |
| Shoot coverage | Establishing images, medium shots, close-ups, shoe inserts and reactions produce editable choices. |
| Match cuts | Right shoe pivot across basketball/dance; teenage Mom to present Mom; remembered care to three living generations. |
| Sound carries the connection | One short English maternal line and an original instrumental score; no invented long explanation of the magic. |
| Review before polishing | Assemble all 26 timed shots, flag continuity defects, then decide which shots deserve final regeneration. |

## Skills et outils / Skills and tools

Local files were found at `/Users/edouardfoussier/code/skills/` (outside this repository). We read `higgsfield-generate/SKILL.md`, its prompt-engineering reference and the product-photoshoot instructions. The downloaded skills target the Higgsfield CLI. The local CLI is not installed; connected MCP tools have their own live schemas and capabilities, so CLI commands are not assumed to be MCP functions.

Generation continues through the connected **Arcads MCP**, using Nano Banana 2 reference images and Kling 3.0 Pro motion. This preserves the existing project and sponsor-credit workflow. We have not trained a Soul ID or executed the CLI product-photoshoot backend.

The installed **Higgsfield video-editing skill** is used for native Higgsedit assembly in its remote sandbox. Audio mixing and delivery checks use FFmpeg. The edit script and exact source mapping are retained with the animatic, rather than treating a prompt as the finished film.

## Choix du premier montage / First-cut choices

- 76 seconds, 26 shots, 16:9, 24 fps; current realistic storyline.
- One original instrumental score and one English voice line, for the mixed-language team.
- A few deliberately static inserts may remain in an animatic. They are identified in the shot map and are not described as generated motion.
- Initials and closing typography are added in the edit for reliable spelling. This is editorial compositing, not proof of handwriting animation.
- Image and video generation can run independently in parallel after each shot's reference is ready. An accepted batch is not evidence of an unlimited backend concurrency limit.
- Final delivery status, actual costs, source choices and known defects belong in `animatic-v1/README.md` and its QA files.

## Prochaine décision créative / Next creative decision

**FR.** Regarder le montage d'une traite avant de discuter des détails. Vérifier d'abord si l'on comprend qui transmet les chaussures, si les trois souvenirs se distinguent et si le retour à la famille émeut. Ensuite seulement, corriger les mains, badges, raccords et sons plan par plan.

**EN.** Watch the cut once without stopping before discussing detail. First check whether the shoe's transmission is clear, whether the three memories read as distinct chapters, and whether returning to the family feels moving. Then fix hands, badges, continuity and sound shot by shot.
