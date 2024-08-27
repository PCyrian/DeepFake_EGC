**22/07**

    - Reminder from the supervisor to keep an update.txt file on Git with daily progress because of remote work.
    - Told to re-test speech-to-speech conversion, justify decisions in writing, and improve TTS sync with video start.
    - Started working on the script to detect the start of speech in videos.
    - Began refactoring code in various units and classes for better structure and clarity.
    - Added comments to the code for better documentation and readability.

---

**23/07**

    - Continued working on the speech detection script.
    - ##Encountered an issue##: the script always records 29 seconds instead of 9. Tried to figure out the issue but no luck yet.
    - Tweaked the UI to include an iteration field for creating multiple output videos in a single request. This should make testing more efficient.
    - More code refactoring and commenting.

---

**24/07**

    - More UI improvements.
    - Added time estimation to the UI to give a better idea of processing times.
    - Documented the UI changes and why they were made.
    - Continued code refactoring and adding comments.
    - Started digging into DeepFaceLab's repo to understand the technologies they use.

---

**25/07**

    - Tried re-testing the speech-to-speech conversion.
    - Still running into errors; the library seems unstable.
    - Decided to pause further testing on speech-to-speech conversion until there's a more stable library version.
    - Wrote down why this decision was made.
    - Kept researching DeepFaceLab's tech, focusing on how they implement things.

---

**26/07**

    - Finalized and tested the UI changes; everything works as expected.
    - Wrote up justifications for each decision made this week, including:
        - The instability of the speech-to-speech conversion library.
        - Adding the iteration field and time estimation in the UI.
        - Issues with the speech detection script.
    - Compiled and committed all updates to the Git repository.
    - Continued looking into DeepFaceLab's tech and documenting findings.
    - Finished code refactoring and made sure all relevant sections are well-commented

---

**29/07**

    - Got new instructions and guidance :
        - As previously mentioned, need to emphasize more on researching alternatives technologies even if they don't exactly fit my our use-case.
        - Keep 3-4 exemple french target audio files, and automate cross-testing between all 12 possible voice combinations.
        - Prepare a video directory in Git, with at least 4 instances per voice combination, good and bad.
        - Further research wav2Lip and babelfish as well as the Sync API as possible technologies as well as other STS models on Huggingface for exemple.
        - If TTS' by Coqui lib failed inference for freevc24, attempt to use the docker version or start on a new clean env.
        - Research https://huggingface.co/nvidia/bigvgan_v2_44khz_128band_512x for post-processing
        - Research https://synclabs.so/ for possible lip-syncing API

---

**08/08**

    - Had a meeting with my mentor. He suggested focusing on lip-syncing as he felt the audio part was good enough for now. I disagreed but will proceed as instructed.  
    - Spent the day updating output file names to prevent overwriting and keep a record of all test outputs.

---

**09/08**  

    - Continued working on Wav2Lip setup.  
    - Realized that Wav2Lip only supports Python 3.6, which wasn't clearly specified in the README.  
    - The initial installation failed due to having the wrong Python version.

---

**10/08**  

    - Installed Python 3.6.0, but ran into another issue: Torch 1.1.0 isn't available for Python 3.6.0.  
    - Considered needing a higher version of Python 3.6, but still unsure of the exact version required.  
    - Spent time searching the issues tab on the Wav2Lip repository for solutions, but most issues were minor and unhelpful.

---

**11/08**  

    - Found an issue in the Wav2Lip repo about running it on Windows. The suggested solution was to use WSL.  
    - Frustrated by the prospect of needing to set up a Linux VM or dual boot just to test part of the project.  
    - Ventured into Linux setup considerations, knowing the pain of dealing with missing DLLs and NVIDIA/CUDA issues on Linux.

---

**12/08**  

    - Debated the best approach to proceed: whether to set up a Linux VM, dual boot, or continue struggling with the Windows setup.  
    - Decided to start the process of setting up a Linux environment while considering potential workarounds for the NVIDIA/CUDA issues.

---

**13/08**  

    - Continued the setup of the Linux environment, working through dependency issues and preparing for potential CUDA/NVIDIA challenges.  
    - Planned to test Wav2Lip on the new setup as soon as everything is configured correctly.
    - Should investigate potential solution : https://github.com/Rudrabha/Wav2Lip/issues/185 though I tried it already.
    - Update, the code appears to have been run on python 3.5.2 or older, then vaguely described as working in newer version best thus the requirement update to "3.6+" than back to 3.6
    - The commit changing the required python version in the readme didn't update the requirements nor the code, nor did any following. Repo might run better in 3.5.6
    - Possible outdated tutorial worth looking into even if it uses google colab instead of being local "https://www.youtube.com/watch?v=Ic0TBhfuOrA"

---

**14/08**

    - meeting with mentor.
    - use anaconda for .venv management
    - resolved issue with old dependencies using pytorch "previous version" page

---

**15/08**

    - updated workstation's setup to accomodate the project and run it more efficiently
    - applied the fix to workstation version too.
    - ran 10 iteration on CPU only, took a very very long time to process.
    - there was an issue with cuda, so laptop and desktop versions run on CPU only
    - all iterations crashed after about an hour of processing.
    - though iterations crashed because of a missing dependency or file not found error,in the temp directory I could find a result.avi file that appears to contain the lipsynced video, but the audio is missing.
    - audio could be manually added using ffmpeg and moviepy to the temp file produced resulting in a final product, though it would be best to fix the crashh.

---

**16/08**

    - researched possible solutions using cuda 12.6 for xTTSv2, and CUDA 10.0 for Wav2Lip processing
    - tried installing both CUDA version, and changing the CUDA env variable in each .venv, without success as CUDA 10 installer fails with no traceback
    - consider trying out the repository's linked docker image.

---

**19/08**

    - installed docker ce after reading a bit of documentation.
    - took a few docker tutorials and watch docker courses
    - tried to build the provided docker image, without sucess.
    - message mentor, awaiting response
    - issue seems to arise because (FROM nvidia/cuda:10.1-cudnn7-devel-ubuntu18.04) reports it cannot find the specified cuda/cudnn/ubuntu image.
    - if image is deprecated by nvidia, which it seemed from my research, it can be a large issue.

---

**20/08**

    - while awaiting response, I updated the excel file on similar projects. Readability was inproved.
    - I am now considering running a virtual machine acting as a server for either the lipsync or TTS generation to resolve dependency issues.
    - our goal for a completely automated pipeline is getting further away though a manual one is already ready.
---

**21/08**

    - Meeting resulted in getting cuda to be installed. Dependencies in conda need to be installed independently one after the other sometimes.
    - The image the docker file was based on is not available anymore. Was told that it was way too much of a hassle to update and to forget docker.

---

**22/08**
    
    - struggled a lot with drivers and dependencies. Watched explanations video about conda and other relevant topics.
    - I managed to run Wav2Lip on its own conda env, and the rest of the project on its own, but from two different entrypoints.

---

**23/08**

    - I managed to run a script from a conda env, and have it launch another script on another env with other dependencies and packages.
    - I got Wav2Lip to install with its dependencies by taking them one by one and letting pip resolve conflicts. CUDA was identified.
    - I wrote a test script fetching if cuda is available, what version, what version of python is running, and what version of pytorch.
    - comfirmed my env setup worked, cuda was detected and comparing cpu to cuda, it was indeed improving performances.
    - Yet, Wav2Lip seemed stuck at the progress bar 0%. I forgot about the window and went to research. Turns out after 5 hours, it was to 16%
    - Wav2Lip with CUDA estimated a completion time of 32 hours instead of 45 minute for CPU only.

---

**26/08**
    
    - researched potential post-processing improvements techniques.
        - Thought to use whisper to create a transcription of generated audio, and quantify accuracy by comparing the transcript to original input.
        - potentially generating 10 speech iteration and using the most accurate one.
    - potential use for a nvidia BigVGAN model (neural vocoder) https://huggingface.co/nvidia/bigvgan_v2_44khz_128band_512x/blob/main/README.md
    - potential upgrade using a xttsv2 + RVC pipeline for audio processing (https://github.com/litagin02/rvc-tts-webui)
    - discussed with colleagues about the CUDA issue I encountered. They were just as baffled as me.
    - They pointed out that some issue was opened and similar to mine. The issue might come from the repo.
    - Most issues of the last year have not been answered or solved. It is becoming concerning.
    - Might have to stick to CPU only after all.
    - Might have a meeting with google researchers on free time, might ask for advice.

