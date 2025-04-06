document.addEventListener('DOMContentLoaded', function() {
    const emotionSelector = document.getElementById('emotionSelector');
    const goalSelector = document.getElementById('goalSelector');
    const outcomeSelector = document.getElementById('outcomeSelector');
    const generateButton = document.getElementById('generateButton');
    const scriptDisplay = document.getElementById('scriptDisplay');
    const audioPlayer = document.getElementById('audioPlayer');
    const audioPlayerContainer = document.getElementById('audioPlayerContainer');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const errorMessage = document.getElementById('errorMessage');
    const copyScriptButton = document.getElementById('copyScriptButton');

    const emotions = ['Happy', 'Sad', 'Anxious', 'Calm', 'Angry', 'Excited'];
    const goals = ['Relaxation', 'Focus', 'Better Sleep', 'Stress Relief'];
    const outcomes = ['Feeling Calm', 'Increased Energy', 'Mental Clarity', 'Emotional Balance'];

    function createTags(items, containerId, baseClass, selectedClass) {
        const container = document.getElementById(containerId);
        items.forEach(item => {
            const tag = document.createElement('button');
            tag.classList.add('tag', ...baseClass.split(' '));
            tag.textContent = item;
            tag.addEventListener('click', () => {
                tag.classList.toggle('selected');
                tag.classList.toggle(...selectedClass.split(' '));
                validateSelections();
            });
            container.appendChild(tag);
        });
    }

    createTags(emotions, 'emotionSelector', 'bg-indigo-100 text-indigo-800 hover:bg-indigo-200', 'bg-indigo-500 text-white');
    createTags(goals, 'goalSelector', 'bg-green-100 text-green-800 hover:bg-green-200', 'bg-green-500 text-white');
    createTags(outcomes, 'outcomeSelector', 'bg-purple-100 text-purple-800 hover:bg-purple-200', 'bg-purple-500 text-white');

    function validateSelections() {
        const selectedEmotions = document.querySelectorAll('#emotionSelector button.selected');
        const selectedGoals = document.querySelectorAll('#goalSelector button.selected');
        const selectedOutcomes = document.querySelectorAll('#outcomeSelector button.selected');

        const emotionContainer = document.getElementById('emotionContainer');
        const goalContainer = document.getElementById('goalContainer');
        const outcomeContainer = document.getElementById('outcomeContainer');

        const isValid = selectedEmotions.length > 0 && selectedGoals.length > 0 && selectedOutcomes.length > 0;

        emotionContainer.classList.toggle('border-red-500', selectedEmotions.length === 0);
        goalContainer.classList.toggle('border-red-500', selectedGoals.length === 0);
        outcomeContainer.classList.toggle('border-red-500', selectedOutcomes.length === 0);

        generateButton.disabled = !isValid;

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

        const selectedEmotions = [...document.querySelectorAll('#emotionSelector button.selected')].map(tag => tag.textContent);
        const selectedGoals = [...document.querySelectorAll('#goalSelector button.selected')].map(tag => tag.textContent);
        const selectedOutcomes = [...document.querySelectorAll('#outcomeSelector button.selected')].map(tag => tag.textContent);

        showLoading(true);
        hideError();

        try {
            console.log('Sending meditation request with:',
                'Emotions:', selectedEmotions,
                'Goals:', selectedGoals,
                'Outcomes:', selectedOutcomes
            );
            
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

            const data = await response.json();
            
            if (!response.ok) {
                let errorMessage = 'Failed to generate meditation';
                
                if (data.error) {
                    errorMessage = data.error;
                } else if (data.message) {
                    errorMessage = data.message;
                }
                
                if (data.validation_errors) {
                    errorMessage = 'Please fix the following issues: ' + data.validation_errors.join(' ');
                }
                
                console.error('API Error:', data);
                throw new Error(errorMessage);
            }

            console.log('Meditation generated successfully:', data);
            displayMeditation(data);
        } catch (error) {
            console.error('Error generating meditation:', error);
            showError('An error occurred: ' + error.message);
            
            // Add retry button if it's a server error
            if (error.message.includes('server') || error.message.includes('unexpected')) {
                addRetryButton();
            }
        } finally {
            showLoading(false);
        }
    });

    function showLoading(isLoading) {
        loadingIndicator.classList.toggle('hidden', !isLoading);
        generateButton.disabled = isLoading;
    }

    function showError(message) {
        errorMessage.querySelector('p:last-child').textContent = message;
        errorMessage.classList.remove('hidden');
        errorMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    function hideError() {
        errorMessage.classList.add('hidden');
        // Remove retry button if it exists
        const retryButton = document.getElementById('retryButton');
        if (retryButton) {
            retryButton.remove();
        }
    }

    function addRetryButton() {
        // Remove existing retry button if present
        const existingButton = document.getElementById('retryButton');
        if (existingButton) {
            existingButton.remove();
        }
        
        // Create new retry button
        const retryButton = document.createElement('button');
        retryButton.id = 'retryButton';
        retryButton.classList.add(
            'mt-4', 'bg-green-500', 'hover:bg-green-600', 'text-white',
            'font-bold', 'py-2', 'px-4', 'rounded-lg', 'transition',
            'duration-300', 'ease-in-out', 'focus:outline-none',
            'focus:ring-2', 'focus:ring-green-500', 'focus:ring-opacity-50'
        );
        retryButton.textContent = 'Try Again';
        retryButton.addEventListener('click', () => {
            hideError();
            generateButton.click();
        });
        
        // Append to error message
        errorMessage.appendChild(retryButton);
    }

    function displayMeditation(data) {
        // Display the script
        document.getElementById('meditationScript').textContent = data.script;
        
        // Display title if available
        const titleElement = document.getElementById('meditationTitle');
        if (titleElement && data.title) {
            titleElement.textContent = data.title;
            titleElement.classList.remove('hidden');
        }
        
        // Display duration if available
        const durationElement = document.getElementById('meditationDuration');
        if (durationElement && data.duration_seconds) {
            const minutes = Math.floor(data.duration_seconds / 60);
            const seconds = data.duration_seconds % 60;
            durationElement.textContent = `Duration: ${minutes}:${seconds.toString().padStart(2, '0')}`;
            durationElement.classList.remove('hidden');
        }
        
        // Set audio source
        audioPlayer.src = data.audio_url;
        
        // Show containers
        scriptDisplay.classList.remove('hidden');
        audioPlayerContainer.classList.remove('hidden');
        
        // Scroll to results
        scriptDisplay.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    copyScriptButton.addEventListener('click', () => {
        const scriptText = document.getElementById('meditationScript').textContent;
        navigator.clipboard.writeText(scriptText).then(() => {
            const originalText = copyScriptButton.textContent;
            copyScriptButton.textContent = 'Copied!';
            copyScriptButton.disabled = true;
            setTimeout(() => {
                copyScriptButton.textContent = originalText;
                copyScriptButton.disabled = false;
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy text: ', err);
        });
    });

    validateSelections();
});
