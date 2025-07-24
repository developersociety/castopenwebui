<script lang="ts">
	import { page } from '$app/stores';
	import { WEBUI_API_BASE_URL } from '$lib/constants';

	import { onMount, getContext } from 'svelte';

	const i18n = getContext('i18n');

	let message = 'Verifying...';
	let status = 'loading';

	onMount(async () => {
		const token = $page.url.searchParams.get('token');
		const res = await fetch(`${WEBUI_API_BASE_URL}/profiles/verify-email?token=${token}`);
		if (res.ok) {
			message = 'Your email has been verified!';
			status = 'success';
		} else {
			const err = await res.json();
			message = err.detail || 'Invalid or expired verification link.';
			status = 'error';
		}
	});
</script>

<div class="absolute w-full h-full flex z-50">
	<div class="absolute rounded-xl w-full h-full backdrop-blur-sm flex justify-center">
		<div class="m-auto pb-44 flex flex-col justify-center">
			<div class="max-w-md">
				<div class="text-center text-2xl font-medium z-50">
					{message}
				</div>

				<div class=" mt-4 text-center text-sm w-full">
					You can now log in to access your account. If your account has already been approved by an
					administrator, you’ll have full access to the system. If you haven’t been approved yet,
					please wait for admin approval before logging in.
					<br class=" " />
					<br class=" " />
				</div>

				<div class=" mt-6 mx-auto relative group w-fit">
					<button
						class="relative z-20 flex px-5 py-2 rounded-full bg-gray-100 hover:bg-gray-200 transition font-medium text-sm"
						on:click={() => {
							location.href = '/';
						}}
					>
						{$i18n.t('Sign in')}
					</button>
				</div>
			</div>
		</div>
	</div>
</div>
