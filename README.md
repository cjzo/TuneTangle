## TuneTangle
Want to break out of the monotonous loop of music that you can't seem to escape? Look no further! **TuneTangle gives you a curated playlist based on your existing taste to spice your music life up!**

## Demo
[Link to Video](https://www.youtube.com/watch?v=vHNyjKSygag)

## Setup
On Windows:
```
cd backend

pip install -r requirements.txt

pip install moviepy

pip install shazamio

python createDB.py

python app.py
```
On Mac, the last two lines would instead be:
```
python3 createDB.py

python3 app.py
```
In a second terminal, run from the base directory:
```
cd frontend

npm install

npm run start
```
## Inspiration
The world of music seems limitless, and yet sometimes, it feels hard to break free from the monotonous music loop that many of us experience. We often find ourselves stuck in a cycle where attempts to discover new songs lead us back to familiar tunes. TuneTangle aims to solve this by leveraging the viral potential of TikTok and the extensive catalog of Spotify to introduce users to fresh, niche music that aligns with their tastes. By integrating sound recognition and recommendation algorithms, we envisioned a tool that not only surfaces new music but also makes the discovery process enjoyable and seamless.

## What it does

TuneTangle is a **song recommendation system** designed for **discovering new music on TikTok**. With TuneTangle, users can find their next favorite tune or viral hit from videos curated just for them.

It can take inputs in many forms: ranging anywhere from short video clips to user playlists. And if a song is just that good, just its name will do the trick. Whatever melody is presented, TuneTangle finds other songs just like it, ensuring the perfect discovery method.

Listeners can easily access these recommendations through a simple and secure Spotify connection, viewing them in a user-friendly environment.

## How we built it
In order to get this project done under the time constraints while also fitting everyone’s schedules, apportioning tasks was critical for our success. We split the project up so that one person worked on the backend, one on researching recommendation systems, and two on the frontend because we prioritized an appealing user experience, attempting to mimic TikTok’s engaging and impactful UI design. 

### 1. Sound Recognition
First, we wanted to implement a sound recognition system to complement the search bar because many sounds on TikTok are “original” sounds that use existing songs without a known tag to identify said song. To do this, we used Python and Shazam.io, an open-source song recognition system, enabling users to not only find the name of the song they like but also find other similar songs.

### 2. Music Recommendation System
On the backend, the Spotify for Developers API was used once the name of a song was given to 
Use the open-source recommendation system to find sonically similar songs
Cross-reference the recommendations with users’ personal playlists to try and maximize the chances that the songs we recommend are actually new discoveries instead of just popular songs.
Add functionality once the recommended songs were given so that users could easily add songs to their “Liked Songs” in Spotify in one click of a button
Furthermore, we knew from personal experience how disappointing the Spotify recommendation system could be, so we tried to fine-tune the system as much as possible by taking data from the user-inputted song such as danceability and liveness and giving a specific range around those values for our recommended songs.

### 3. Designing the Frontend
On the frontend, we utilized a React framework and used Chakra UI and Typescript to make our code as robust and maintainable as possible. The combination of these technologies allowed us to create a responsive and visually appealing user interface, ensuring that users have a smooth and enjoyable experience while discovering new music through TikTok. By having a modular design, future developments would be easy to implement with little of the original code being affected.

### 4. Catering to User Experience
We aimed to have a modern style user interface with a sleek yet comfortable appearance. Thus, we opted for a dark and muted website background with an intentional high-contrast color palette for user accessibility, highlighting actions and the cursor. Smooth transition animations were added for a responsive UI feeling, and large buttons and wide input fields were used to draw user attention.

We imitated the TikTok experience with our video recommendation results by creating a vertical feed of cards with TikTok videos embedded. Additionally, we designed the website navigation to be as intuitive as possible, allowing for straightforward usage of the app.

### 5. Client ↔ Server
To communicate the results to the user, get updates from the Flask API from our server using our React web app. The communication to the flask endpoints from the frontend initiates by providing the user’s authentication token to generate music recommendations. After processing the request and calling various APIs such as Spotify, TikAPI, and ShazamIO, the server returns a json of information that is then processed and displayed in an engaging format.

## Challenges we ran into

We dedicated a significant amount of time to planning a friendly user experience. On the backend, we debated how to utilize the results of our TikTok video search after determining music recommendations. Decisions such as downloading the videos versus embedding them were crucial, as they would ultimately dictate the flow of the app. Additionally, we aimed to replicate the TikTok environment as closely as possible, which led us to question the validity of TikAPI. To ensure practicality in a future integrated environment within the TikTok application, we settled on providing a realistic result by embedding TikTok videos.

Even more difficult decisions were essential in creating a seamless and intuitive experience for users, aligning our app closely with the TikTok interface they are familiar with. Displaying video in a feed-like format was essential to mirroring prior experiences. Additionally, we dedicated lots of effort to make the application more efficient timewise. Since searching playlists to create a better recommendation result requires more time, we aimed to use SQL and indexing names to eliminate duplicates. 

## What we learned

The importance of presentation for user interactions can make or break a person’s experience (for example, a list of songs vs. list of TikTok links vs. TikTok video feed). Subsequently, this impacts virality and engagement with the media.

## Accomplishments that we're proud of

Anyone can make a get or post request on an API. What makes projects, however, is how a team can put those pieces together in a cohesive manner that can help people in a way they need. First and foremost, we’re proud to have solved a problem that we personally experience in our lives today, and this product is something that we will use even after this TechJam. 

In addition, creating a complete user experience is something that we never prioritized in our own personal projects until now. After countless iterations and brainstorming, the satisfaction when using our UI is something we are definitely proud of as a team.

## What's next for TuneTangle

We all know the AI buzzword has been flying around the tech space a little too loosely in the modern day. However, we truly believe that utilizing AI in our music recommendation systems can lead to more tailored results that is better than whatever is behind the Spotify API. Perhaps aggregating information that TikTok has aggregated on user music privileges could be helpful as it allows for an analysis of key moments of virality of songs (for example a catchy hook or a funny line) and predict what songs would appeal to audiences sooner. 

Additionally, integrating into the TikTok platform would allow for a much more streamlined experience for users, allowing them to perhaps press a Share->See Similar Songs button instead of having to go to a website and search for songs or download it to their local device to share.

All in all, the possibilities for TuneTangle are **endless**, and we are excited to push the possibilities of Artist Discovery!
