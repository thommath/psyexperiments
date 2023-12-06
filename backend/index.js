require("dotenv").config();

const express = require("express");
const helmet = require("helmet"); // for safety https://helmetjs.github.io/
const cors = require("cors");
const { rateLimit } = require("express-rate-limit");
const app = express();

const axios = require("axios");
const strftime = require("strftime");

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
app.set("trust proxy", "loopback"); // specify a single subnet
// app.use(express.urlencoded({ extended: true })); // TODO: check it out
app.use(cors(corsOptions));

console.log("Hello");

app.get("/", (req, res) => {
  res.send("Hello World to the browser!");
});

app.post("/", (req, res) => {
  // TODO: check body size, once HTTPS is set up it will be redundant
  console.log(req.body);
  console.log(req.query);
  res.send("POST gotten");
  (async () => {
    const result = await uploadDataToOSF(req.body);
    console.log(result ? "Uploaded to OSF" : "Failed to upload to OSF");
  })();
});

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`);
});

async function uploadDataToOSF(data) {
  const provider = "osfstorage";
  const fileName = strftime("%Y%m%d%H%M%S.json", new Date());
  const body = JSON.stringify(data);

  const url = `https://files.osf.io/v1/resources/${process.env.OSF_RESOURCE_ID}/providers/${provider}/?kind=file&name=${fileName}`;
  const headers = {
    "Content-Type": "application/octet-stream",
    Authorization: `Bearer ${process.env.OSF_API_TOKEN}`,
  };

  try {
    const res = await axios.put(url, body, { headers });
    console.log(res.data);
    console.log(`Response status code: ${res.statusCode} for file ${fileName}`);
    return res.statusCode === undefined && res.data !== undefined;
  } catch (error) {
    console.error("Error uploading file:", error);
    return false;
  }
}
