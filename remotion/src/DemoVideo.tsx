import React from 'react';
import {
	AbsoluteFill,
	interpolate,
	spring,
	useCurrentFrame,
	useVideoConfig,
} from 'remotion';

export const DemoVideo: React.FC = () => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();

	const titleOpacity = interpolate(frame, [0, 25], [0, 1], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});

	const titleY = spring({
		frame,
		fps,
		from: 40,
		to: 0,
		config: {
			damping: 200,
		},
	});

	const subtitleOpacity = interpolate(frame, [25, 50], [0, 1], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});

	const cameraDrift = interpolate(frame, [0, 150], [0, -30], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});

	const backgroundOpacity = interpolate(frame, [0, 15], [0, 1], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});

	return (
		<AbsoluteFill
			style={{
				backgroundColor: '#0b0b12',
				opacity: backgroundOpacity,
			}}
		>
			<AbsoluteFill
				style={{
					justifyContent: 'center',
					alignItems: 'center',
					transform: `translateX(${cameraDrift}px) scale(1.05)`,
				}}
			>
				<div
					style={{
						fontFamily: 'Arial, Helvetica, sans-serif',
						fontSize: 96,
						fontWeight: 800,
						color: '#ffffff',
						letterSpacing: 6,
						opacity: titleOpacity,
						transform: `translateY(${titleY}px)`,
					}}
				>
					AI VIDEO STUDIO
				</div>

				<div
					style={{
						marginTop: 32,
						fontFamily: 'Arial, Helvetica, sans-serif',
						fontSize: 36,
						fontWeight: 400,
						color: '#a3a3b8',
						opacity: subtitleOpacity,
					}}
				>
					Première vidéo générée automatiquement
				</div>
			</AbsoluteFill>
		</AbsoluteFill>
	);
};
