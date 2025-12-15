const express = require("express");
const cors = require("cors");
const apiRoutes = require("./routes/apiRoutes");
require("dotenv").config();

const app = express();
const PORT = 5000;

// Middleware
app.use(express.json({ limit: "50mb" }));
app.use(cors());

// Routes
app.use("/", apiRoutes);

// Start Server
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
    console.log(`Thinking Machine is Ready! 🚀`);
});