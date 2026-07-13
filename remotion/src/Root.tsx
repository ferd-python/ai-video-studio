import React from 'react';
import {Composition} from 'remotion';
import {DemoVideo} from './DemoVideo';
import {DynamicVideo} from './compositions/DynamicVideo';
import {getTotalDurationInFrames, getVideoDimensions, loadScenes} from './data/loadScenes';

export const RemotionRoot: React.FC = () => {
	const {project} = loadScenes();
	const {width, height} = getVideoDimensions();
	const dynamicDurationInFrames = getTotalDurationInFrames(project.fps);

	return (
		<>
			<Composition
				id="DemoVideo"
				component={DemoVideo}
				durationInFrames={150}
				fps={30}
				width={1920}
				height={1080}
			/>
			<Composition
				id="DynamicVideo"
				component={DynamicVideo}
				durationInFrames={dynamicDurationInFrames}
				fps={project.fps}
				width={width}
				height={height}
			/>
		</>
	);
};
