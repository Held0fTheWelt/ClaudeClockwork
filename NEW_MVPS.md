Description

We want to compact the codebase to not splatter around the complete project, because it will be implemented into other big projects, that were meant to do complete other things.
To be able to simply plug Claude Clockwork in and to have more hygiene in this project, make a plan for the following tasks.

Main Tasks

- Everything, that needs to be included in other projects resides inside the .claude folder
- old development pipeline in .claude-development should be translated to \mvps and \roadmaps as legacy documentation
- duplicate files that only act as pointers should be eliminated. Additional information in files of the same type should be combined into one file only, no duplicate 
- References need to be updated

Afterwards:
- Legacy pipelines shouldn't exist
- Make a plan to update legacy content to Greenfield content
- make it modern and matching to the anthropic 
- Make implementation MVPs for still unimplemented skills

Afterwards:
- Check, if a new skill could be invented by what has been done, or done again.