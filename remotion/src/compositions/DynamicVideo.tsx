import React from 'react';
import {AbsoluteFill, Sequence, useVideoConfig} from 'remotion';
import {Scene} from '../components/Scene';
import {loadScenes} from '../data/loadScenes';

export const DynamicVideo: React.FC = () => {
	const {fps} = useVideoConfig();
	const {scenes} = loadScenes();

	let startFrame = 0;

	return (
		<AbsoluteFill>
			{scenes.map((scene) => {
				const durationInFrames = scene.duration * fps;
				const from = startFrame;
				startFrame += durationInFrames;

				return (
					<Sequence key={scene.id} from={from} durationInFrames={durationInFrames}>
						<Scene
							title={scene.title}
							text={scene.text}
							duration={scene.duration}
							media={scene.media}
							animation={scene.animation}
							transition={scene.transition}
						/>
					</Sequence>
				);
			})}
		</AbsoluteFill>
	);
};
