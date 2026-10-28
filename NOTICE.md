# Attribution and third-party notice

This repository contains **no third-party skill content**. It ships a router plus a
routing table that refers to expert skills by directory name. You obtain and
install those experts yourself, under their own licences.

The routing table's vocabulary was shaped by these upstream collections. They were
not copied, excerpted, or bundled here — no upstream `SKILL.md`, reference file,
or script is redistributed in this repository.

| Upstream collection | Licence | Used for |
|---|---|---|
| [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | MIT | Expert names and capability boundaries referenced by the routing table |
| [Orchestra-Research/AI-Research-SKILLs](https://github.com/Orchestra-Research/AI-Research-SKILLs) | MIT | Expert names and capability boundaries referenced by the routing table |
| [jaccen/Awesome-Gaussian-Skills](https://github.com/jaccen/Awesome-Gaussian-Skills) | Apache-2.0 | 3D Gaussian Splatting expert names referenced by the routing table |
| [huggingface/skills](https://github.com/huggingface/skills) | Apache-2.0 | Dataset-viewer expert name referenced by the routing table |

## If you redistribute experts

Installing an expert locally for your own use is one thing; republishing its
content is another. If you publish a bundle of experts, you must satisfy each
upstream licence — typically the MIT or Apache-2.0 copyright and permission
notice, and for Apache-2.0 any `NOTICE` file — and you own that compliance work.

## Trademarks

Product and project names are used descriptively. No affiliation with, or
endorsement by, the upstream maintainers is implied.

## Security posture stated plainly

A skill is a prompt artifact that becomes instructions an agent follows with
whatever permissions it already has. Review any expert you point this router at
the way you would review code you run, and treat upstream examples — curl
installers, `--host 0.0.0.0`, mirror redirects, cache deletion, `trust_remote_code`
— as sample text awaiting judgement, not as authorized operations.
