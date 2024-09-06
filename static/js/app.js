document.addEventListener('DOMContentLoaded', function() {
    const emotionSelector = document.getElementById('emotionSelector');
    const goalSelector = document.getElementById('goalSelector');
    const outcomeSelector = document.getElementById('outcomeSelector');
    const generateButton = document.getElementById('generateButton');
    const scriptDisplay = document.getElementById('scriptDisplay');
    const audioPlayer = document.getElementById('audioPlayer');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const errorMessage = document.getElementById('errorMessage');

    const emotions = ['Happy', 'Sad', 'Anxious', 'Calm', 'Angry', 'Excited'];
    const goals = ['Relaxation', 'Focus', 'Better Sleep', 'Stress Relief'];
    const outcomes = ['Feeling Calm', 'Increased Energy', 'Mental Clarity', 'Emotional Balance'];

    function createTags(items, containerId, baseClass) {
        const container = document.getElementById(containerId);
        items.forEach(item => {
            const tag = document.createElement('button');
            tag.classList.add(...baseClass.split(' '), 'transition', 'duration-300', 'ease-in-out', 'transform', 'hover:scale-105');
            tag.textContent = item;
            tag.addEventListener('click', () => {
                tag.classList.toggle('bg-blue-500');
                tag.classList.toggle('text-white');
                validateSelections();
            });
            container.appendChild(tag);
        });
    }

    createTags(emotions, 'emotionSelector', 'px-4 py-2 rounded-full border-2 border-blue-500 text-blue-500 hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50');
    createTags(goals, 'goalSelector', 'px-4 py-2 rounded-full border-2 border-green-500 text-green-500 hover:bg-green-100 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-opacity-50');
    createTags(outcomes, 'outcomeSelector', 'px-4 py-2 rounded-full border-2 border-purple-500 text-purple-500 hover:bg-purple-100 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-opacity-50');

    function validateSelections() {
        const selectedEmotions = document.querySelectorAll('#emotionSelector button.bg-blue-500');
        const selectedGoals = document.querySelectorAll('#goalSelector button.bg-blue-500');
        const selectedOutcomes = document.querySelectorAll('#outcomeSelector button.bg-blue-500');

        const emotionContainer = document.getElementById('emotionContainer');
        const goalContainer = document.getElementById('goalContainer');
        const outcomeContainer = document.getElementById('outcomeContainer');

        const isValid = selectedEmotions.length > 0 && selectedGoals.length > 0 && selectedOutcomes.length > 0;

        emotionContainer.classList.toggle('border-red-500', selectedEmotions.length === 0);
        goalContainer.classList.toggle('border-red-500', selectedGoals.length === 0);
        outcomeContainer.classList.toggle('border-red-500', selectedOutcomes.length === 0);

        generateButton.disabled = !isValid;
        generateButton.classList.toggle('opacity-50', !isValid);
        generateButton.classList.toggle('cursor-not-allowed', !isValid);
        generateButton.classList.toggle('bg-blue-500', isValid);
        generateButton.classList.toggle('bg-gray-400', !isValid);

        const instructions = document.getElementById('selectionInstructions');
        if (!isValid) {
            instructions.textContent = 'Please select at least one option from each category to enable the Generate Meditation button.';
            instructions.classList.remove('hidden');
        } else {
            instructions.classList.add('hidden');
        }

        return isValid;
    }

    generateButton.addEventListener('click', async () => {
        if (!validateSelections()) {
            showError('Please select at least one emotion, goal, and outcome.');
            return;
        }

        const selectedEmotions = [...document.querySelectorAll('#emotionSelector button.bg-blue-500')].map(tag => tag.textContent);
        const selectedGoals = [...document.querySelectorAll('#goalSelector button.bg-green-500')].map(tag => tag.textContent);
        const selectedOutcomes = [...document.querySelectorAll('#outcomeSelector button.bg-purple-500')].map(tag => tag.textContent);

        showLoading(true);
        hideError();

        try {
            const response = await fetch('/api/generate-meditation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    emotions: selectedEmotions,
                    goals: selectedGoals,
                    outcomes: selectedOutcomes
                }),
            });

            if (!response.ok) {
                throw new Error('Failed to generate meditation');
            }

            const data = await response.json();
            displayMeditation(data);
        } catch (error) {
            console.error('Error:', error);
            showError('An error occurred: ' + error.message);
        } finally {
            showLoading(false);
        }
    });

    function showLoading(isLoading) {
        loadingIndicator.classList.toggle('hidden', !isLoading);
        generateButton.disabled = isLoading;
        generateButton.classList.toggle('opacity-50', isLoading);
        generateButton.classList.toggle('cursor-not-allowed', isLoading);
    }

    function showError(message) {
        errorMessage.querySelector('p:last-child').textContent = message;
        errorMessage.classList.remove('hidden');
        errorMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    function hideError() {
        errorMessage.classList.add('hidden');
    }

    function displayMeditation(data) {
        document.getElementById('meditationScript').textContent = data.script;
        audioPlayer.src = data.audio_url;
        scriptDisplay.classList.remove('hidden');
        audioPlayer.classList.remove('hidden');
    }

    validateSelections();
});
