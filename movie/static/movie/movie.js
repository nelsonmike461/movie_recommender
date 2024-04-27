document.addEventListener("DOMContentLoaded", () => {
  // Function to capitalize the first letter of each word in a string
  function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
  }

  // Function to capitalize genres
  function capitalizeGenres(genres) {
    return genres.split(" ").map(capitalizeFirstLetter).join(" ");
  }

  // Function to fetch movie details and display them
  async function displayMovieDetails(imdbId, card) {
    try {
      const response = await fetch(`/details/${imdbId}/`);
      if (!response.ok) {
        throw new Error("Failed to fetch movie details");
      }

      const details = await response.json();

      // Check if the screen size is phone
      const isPhone = window.matchMedia("(max-width: 37.5em)").matches;

      // Update movie details container based on screen size
      if (isPhone) {
        const mobDetailsHtml = phoneDetailsHtml(details);
        updateMobileDetails(mobDetailsHtml, card);
      } else {
        const detailsHtml = createDetailsHtml(details);
        updateMovieDetails(detailsHtml, card);
      }

      // Add and Remove Movie from watchlist
      const addToWatchlistBtn = document.querySelector(".btn__watched");
      if (addToWatchlistBtn) {
        addToWatchlistBtn.addEventListener("click", async (event) => {
          event.preventDefault(); // Prevent the default action
          event.stopPropagation();
          try {
            const response = await fetch(`/toggle_watchlist/${imdbId}/`);
            if (!response.ok) {
              throw new Error("Failed to toggle movie in watchlist");
            }
            const data = await response.json();
            addToWatchlistBtn.textContent =
              data.status === "added" ? "Remove" : "Add to Watchlist";
            if (data.status === "added") {
              card.style.opacity = 0;
              setTimeout(() => card.remove(), 700);
            }
          } catch (error) {
            console.error("Error toggling movie in watchlist:", error);
          }
        });
      }
    } catch (error) {
      console.error("Error fetching movie details:", error);
    }
  }

  // Function to create HTML for movie details
  function createDetailsHtml(details) {
    return `
      <div class="details">
        <div class="top">
          <img class="movie__img" src="https:image.tmdb.org/t/p/original/${
            details.poster
          }">
          <div class="movie__trg">
            <h4 class="movie__title">${details.title}</h4>
            <p class="gr"><span>Genres:</span> ${capitalizeGenres(
              details.genres
            )}</p>
            <p class="gr"><span>Rating:</span> ${details.ratings}</p>
          </div>
        </div>
        <div class="overview">
          <p class="card-text">Language: ${details.language}</p>
          <span class="card-text">Year: ${details.release_date}</span>
          <p class="card-text">${details.overview}</p>
          <button class="btn__watched" data-imdb-id="${
            details.id
          }">Add to Watchlist</button>
        </div>
      </div>
    `;
  }

  // Function to create HTML for movie details for phone layout
  function phoneDetailsHtml(details) {
    return `
      <div class="mobile__details">
        <div class="overview">
          <p class="card-text">Language: ${details.language}</p>
          <span class="card-text">Year: ${details.release_date}</span>
          <p class="card-text">${details.overview}</p>
          <button class="btn__watched" data-imdb-id="${details.id}">Add to Watchlist</button>
        </div>
      </div>
    `;
  }

  // Function to update movie details in the DOM for desktop/tablet layout
  function updateMovieDetails(detailsHtml) {
    const movieDetailsContainer = document.querySelector(".movie__details");
    movieDetailsContainer.innerHTML = detailsHtml;
  }

  // Function to update movie details in the DOM for mobile layout
  function updateMobileDetails(detailsHtml, card) {
    const mobileDetailsContainer = card.querySelector(".mobile__details");
    mobileDetailsContainer.innerHTML = detailsHtml;
  }

  // Event listener for movie card clicks
  const movieCards = document.querySelectorAll(".movie__card");
  movieCards.forEach((card) => {
    card.addEventListener("click", () => {
      const imdbId = card.dataset.imdbId;
      const detailsContainer = card.querySelector(".mobile__details");

      // If the details are already displayed, hide them
      if (detailsContainer.style.display === "block") {
        detailsContainer.style.display = "none";
      } else {
        // Otherwise, fetch and display the details
        displayMovieDetails(imdbId, card);
        detailsContainer.style.display = "block";
      }
    });
  });

  // Event listener for generating recommendations button click
  const generateRecommendationsBtn = document.getElementById(
    "generate-recommendations-btn"
  );
  generateRecommendationsBtn.addEventListener("click", () => {
    document.getElementById("generate-recommendations-form").submit();
  });

  // Remove Movie from the Watchlist
  document.querySelectorAll(".delete-btn").forEach(function (button) {
    button.addEventListener("click", function (e) {
      e.preventDefault();
      var imdb_id = this.dataset.imdbId;
      fetch(`/delete/${imdb_id}/`, {
        method: "POST",
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error("Network response was not ok");
          }
          // Remove the entire card from the DOM
          let card = this.closest(".watchlist__card");
          card.style.opacity = "0";
          setTimeout(() => card.remove(), 600);
        })
        .catch((error) => {
          console.error(
            "There has been a problem with your fetch operation:",
            error
          );
        });
    });
  });

  window.onload = function () {
    if (window.location.pathname == "/watchlist") {
      var button = document.querySelector(".recommendation-btn");
      button.classList.add("hidden");
    }
  };
});
