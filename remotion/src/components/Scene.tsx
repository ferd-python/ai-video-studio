import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import type {SceneData} from '../data/loadScenes';

type SceneProps = Pick<
	SceneData,
	'title' | 'text' | 'duration' | 'media' | 'animation' | 'transition'
>;

export const Scene: React.FC<SceneProps> = ({title, text}) => {
	const frame = useCurrentFrame();

	const opacity = interpolate(frame, [0, 20], [0, 1], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});

	return (
		<AbsoluteFill
			style={{
				backgroundColor: '#0b0b12',
				justifyContent: 'center',
				alignItems: 'center',
			}}
		>
			<div
				style={{
					opacity,
					display: 'flex',
					flexDirection: 'column',
					alignItems: 'center',
					fontFamily: 'Arial, Helvetica, sans-serif',
					color: '#ffffff',
					textAlign: 'center',
					padding: '0 120px',
				}}
			>
				<div style={{fontSize: 64, fontWeight: 800, marginBottom: 24}}>
					{title}
				</div>
				<div style={{fontSize: 32, fontWeight: 400, color: '#a3a3b8'}}>
					{text}
				</div>
			</div>
		</AbsoluteFill>
	);
};
