<script>
  export let value = null; // The selected charity object (two-way bound in parent)
  export let placeholder = 'Search charity...';

  import { getCharities } from '$lib/apis/charities';

  let query = '';
  let suggestions = [];
  let debounce;

  // When value changes from the parent, reset query
  $: if (value) query = value.name;

  async function fetchCharities(q) {
    const res = await getCharities(q);
    suggestions = res.charities;
  }

  $: if (query.length > 1 && !value) {
    clearTimeout(debounce);
    debounce = setTimeout(() => fetchCharities(query), 150);
  } else if (!value) {
    suggestions = [];
  }

  function selectCharity(charity) {
    value = charity;
    query = charity.name;
    suggestions = [];
  }
  function handleInput(e) {
    query = e.target.value;
    if (value && query !== value.name) value = null;
  }
  function clearCharity() {
    value = null;
    query = '';
    suggestions = [];
  }
</script>

  {#if value}
    <div class="flex items-center bg-gray-100 rounded px-2 py-1">
      <span class="flex-1 text-sm">{value.name}</span>
      <button
        class="ml-2 text-gray-400 hover:text-gray-700"
        on:click={clearCharity}
        title="Clear"
      >×</button>
    </div>
  {:else}
    <input
      class="w-full text-sm bg-transparent outline-hidden"
      type="text"
      bind:value={query}
      placeholder={placeholder}
      autocomplete="off"
      on:input={handleInput}
    />

    {#if suggestions.length}
      <ul class="border border-gray-200 bg-white max-h-48 overflow-y-auto rounded shadow mt-1">
        {#each suggestions as charity}
          <li
            class="px-3 py-1 hover:bg-gray-100 cursor-pointer"
            on:click={() => selectCharity(charity)}
          >{charity.name}</li>
        {/each}
      </ul>
    {/if}
  {/if}
