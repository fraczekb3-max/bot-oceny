const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');

const app = express();
app.use(express.json());
app.use(cors());

// Połączenie z bazą danych MongoDB (wklej swój link w cudzysłowie)
const MONGO_URL = process.env.MONGO_URL || 'TUTAJ_WKLEJ_SWOJ_LINK_DO_BAZY_DANYCH';

mongoose.connect(MONGO_URL)
    .then(() => console.log('Połączono z bazą MongoDB! 🚀'))
    .catch(err => console.error('Błąd połączenia z bazą:', err));

// Schemat posta w bazie danych
const PostSchema = new mongoose.Schema({
    title: { type: String, required: true },
    content: { type: String, required: true },
    category: { type: String, default: 'Ogólne' },
    date: { type: Date, default: Date.now }
});

const Post = mongoose.model('Post', PostSchema);

// Endpoint do pobierania wszystkich postów
app.get('/api/posts', async (req, res) => {
    try {
        const posts = await Post.find().sort({ date: -1 });
        res.json(posts);
    } catch (err) {
        res.status(500).json({ error: 'Nie udało się pobrać postów' });
    }
});

// Endpoint do dodawania nowego posta
app.post('/api/posts', async (req, res) => {
    try {
        const { title, content, category } = req.body;
        const newPost = new Post({ title, content, category });
        await newPost.save();
        res.status(201).json({ message: 'Post dodany pomyślnie!', post: newPost });
    } catch (err) {
        res.status(400).json({ error: 'Nie udało się dodać posta' });
    }
});

// Uruchomienie serwera na porcie przypisanym przez Railway lub 3000
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Serwer działa na porcie ${PORT}`);
});
