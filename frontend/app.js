// GANTI BAGIAN INI DENGAN DOMAIN KAMU NANTI!
const DOMAIN = "@domainmu.com"; 

// URL Backend FastAPI kamu
const API_BASE_URL = window.location.origin + "/api/inbox";

let currentEmail = "";
let currentInboxData = [];
let pollingInterval;

// --- LOGIKA DARK MODE (AUTO SISTEM) ---
const html = document.documentElement;
const themeToggleBtn = document.getElementById('theme-toggle');
const iconDark = document.getElementById('icon-dark');
const iconLight = document.getElementById('icon-light');

// Fungsi untuk mengubah UI berdasarkan status Dark/Light
function updateThemeUI(isDark) {
    if (isDark) {
        html.classList.add('dark');
        iconDark.classList.add('hidden');
        iconLight.classList.remove('hidden');
    } else {
        html.classList.remove('dark');
        iconLight.classList.add('hidden');
        iconDark.classList.remove('hidden');
    }
}

// 1. Cek mode default bawaan sistem (Laptop/HP pengguna) saat web dibuka
const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
updateThemeUI(systemPrefersDark);

// 2. Jika tombol bulan/matahari ditekan manual
themeToggleBtn.addEventListener('click', () => {
    const isDarkNow = html.classList.contains('dark');
    updateThemeUI(!isDarkNow);
});

// 3. Jika pengguna mengubah setelan sistem saat web sedang terbuka, otomatis ganti!
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
    updateThemeUI(event.matches);
});
// --------------------------------------

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById('domain-label').innerText = DOMAIN;
});

function generateRandomEmail() {
    const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
    let result = 'meow_';
    for (let i = 0; i < 6; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result + DOMAIN;
}

function init() {
    changeEmail();
}

function changeEmail() {
    currentEmail = generateRandomEmail();
    document.getElementById('email-address').value = currentEmail;
    
    closeEmailViewer();
    renderInbox([]); 
    
    if (pollingInterval) clearInterval(pollingInterval);
    fetchInbox(); 
    pollingInterval = setInterval(fetchInbox, 5000); 
}

function setCustomEmail() {
    const inputElement = document.getElementById('custom-username');
    let customName = inputElement.value.trim();

    if (!customName) {
        alert("Ketik dulu nama email yang kamu mau!");
        return;
    }

    customName = customName.replace(/[^a-zA-Z0-9._-]/g, '').toLowerCase();
    currentEmail = customName + DOMAIN;
    
    document.getElementById('email-address').value = currentEmail;
    inputElement.value = ""; 

    closeEmailViewer();
    renderInbox([]); 

    if (pollingInterval) clearInterval(pollingInterval);
    fetchInbox(); 
    pollingInterval = setInterval(fetchInbox, 5000); 
}

function copyToClipboard() {
    const emailInput = document.getElementById('email-address');
    emailInput.select();
    document.execCommand('copy');
    
    const statusText = document.getElementById('copy-status');
    statusText.classList.remove('hidden');
    setTimeout(() => {
        statusText.classList.add('hidden');
    }, 3000);
}

// --- FUNGSI FETCH YANG SUDAH DITAMBAHKAN PROTEKSI LOGIN ---
async function fetchInbox() {
    if (!currentEmail) return;
    
    const spinner = document.getElementById('loading-spinner');
    spinner.classList.remove('hidden');

    try {
        const response = await fetch(`${API_BASE_URL}/${currentEmail}`);
        
        // Cek jika API menolak akses karena belum login atau token expired
        if (response.status === 401) {
            clearInterval(pollingInterval); // Hentikan auto-refresh
            alert("Sesi login kamu telah berakhir. Silakan login kembali.");
            window.location.reload(); // Reload web agar diarahkan ke halaman login
            return;
        }

        const result = await response.json();
        
        if (result.status === "success") {
            if (result.data.length !== currentInboxData.length) {
                currentInboxData = result.data;
                renderInbox(currentInboxData);
            }
        }
    } catch (error) {
        console.error("Gagal mengambil data:", error);
    } finally {
        setTimeout(() => spinner.classList.add('hidden'), 500);
    }
}

function renderInbox(emails) {
    const listContainer = document.getElementById('inbox-list');
    
    if (emails.length === 0) {
        listContainer.innerHTML = `<div class="p-8 text-center text-gray-500 dark:text-gray-400">
            <i class="fa-solid fa-cat text-4xl mb-3 opacity-50 block"></i>
            Kotak masuk kosong. Menunggu pesan masuk...
        </div>`;
        return;
    }

    let htmlData = '';
    emails.forEach((email, index) => {
        htmlData += `
            <div onclick="openEmail(${index})" class="p-4 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer transition flex items-center justify-between">
                <div class="flex-1 min-w-0">
                    <p class="text-sm font-semibold text-gray-900 dark:text-white truncate">${email.sender}</p>
                    <p class="text-sm text-gray-500 dark:text-gray-400 truncate">${email.subject || '(Tanpa Subjek)'}</p>
                </div>
                <div class="text-xs text-gray-400 dark:text-gray-500 ml-4">
                    Baru saja
                </div>
            </div>
        `;
    });
    listContainer.innerHTML = htmlData;
}

function openEmail(index) {
    const email = currentInboxData[index];
    if (!email) return;

    document.getElementById('view-subject').innerText = email.subject || "(Tanpa Subjek)";
    document.getElementById('view-sender').innerText = email.sender;
    
    const iframe = document.getElementById('view-body');
    const content = email.body_html || `<pre style="font-family: sans-serif; white-space: pre-wrap; padding: 20px;">${email.body_text}</pre>`;
    iframe.srcdoc = content;

    document.getElementById('email-viewer').classList.remove('hidden');
    document.getElementById('email-viewer').scrollIntoView({ behavior: 'smooth' });
}

function closeEmailViewer() {
    document.getElementById('email-viewer').classList.add('hidden');
}

// --- FUNGSI LOGOUT YANG DIPINDAHKAN DARI HTML ---
window.logoutNekomail = async function() {
    try {
        await fetch('/api/logout', { method: 'POST' });
        window.location.reload(); 
    } catch (error) {
        console.error("Gagal logout:", error);
        alert("Terjadi kesalahan saat logout.");
    }
}

window.onload = init;
