const express = require("express");
const helmet = require("helmet"); // for safety https://helmetjs.github.io/
const cors = require("cors");
const { rateLimit } = require("express-rate-limit");
const app = express();

const port = 3001; // should be different from frontend

var corsOptions = {
  origin:
    process.env.NODE_ENV === "production"
      ? "http://158.37.63.194/"
      : "http://localhost:3000",
  optionsSuccessStatus: 200, // some legacy browsers (IE11, various SmartTVs) choke on 204
};

const limiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 60 minutes
  limit: 100, // Limit each IP to 100 requests per `window` (here, per 60 minutes).
  standardHeaders: "draft-7", // draft-6: `RateLimit-*` headers; draft-7: combined `RateLimit` header
  legacyHeaders: false, // Disable the `X-RateLimit-*` headers.
});

// Apply the rate limiting middleware to all requests.
app.use(limiter);

app.use(helmet());
app.use(express.json());
// app.use(express.urlencoded({ extended: true })); // TODO: check it out
app.use(cors(corsOptions));

app.get("/api", (req, res) => {
  res.send("Hello World to the browser!");
});

app.post("/api", (req, res) => {
  // TODO: check body size, once HTTPS is set up it will be redundant
  console.log(req.body);
  console.log(req.query);
  res.send("POST gotten");
});

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`);
});
