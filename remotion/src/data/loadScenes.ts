import sceneData from '../../../workflow/scene_schema.json';

export type MediaType = 'image' | 'video';

export interface SceneMedia {
	type: MediaType;
	path: string;
}

export interface SceneData {
	id: number;
	duration: number;
	title: string;
	text: string;
	media: SceneMedia;
	animation: string;
	transition: string;
}

export interface ProjectData {
	title: string;
	format: 'horizontal' | 'vertical';
	resolution: string;
	fps: number;
}

export interface SceneSchema {
	project: ProjectData;
	scenes: SceneData[];
}

const RESOLUTIONS: Record<string, {width: number; height: number}> = {
	'4K': {width: 3840, height: 2160},
	FullHD: {width: 1920, height: 1080},
	HD: {width: 1280, height: 720},
};

export const loadScenes = (): SceneSchema => {
	return sceneData as SceneSchema;
};

export const getTotalDurationInFrames = (fps: number): number => {
	const {scenes} = loadScenes();
	return scenes.reduce((total, scene) => total + scene.duration * fps, 0);
};

export const getVideoDimensions = (): {width: number; height: number} => {
	const {project} = loadScenes();
	const base = RESOLUTIONS[project.resolution] ?? RESOLUTIONS.FullHD;

	if (project.format === 'vertical') {
		return {width: base.height, height: base.width};
	}

	return base;
};
