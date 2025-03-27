#!/bin/bash
set -eo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

cleanup() {
    log_warning "⚠️ ʀᴇᴄᴇɪᴠᴇᴅ ꜱʜᴜᴛᴅᴏᴡɴ ꜱɪɢɴᴀʟ, ᴛᴇʀᴍɪɴᴀᴛɪɴɢ ᴘʀᴏᴄᴇꜱꜱᴇꜱ..."
    kill -TERM ${GUNICORN_PID} 2>/dev/null || true
    kill -TERM ${VX_PID} 2>/dev/null || true
    exit 0
}

start_services() {
    PORT=${PORT:-8080}
    
    log_info "ꜱᴛᴀʀᴛɪɴɢ ᴠx ᴀɪ ᴀᴘɪ ꜱᴇʀᴠᴇʀ ᴡɪᴛʜ ɢᴜɴɪᴄᴏʀɴ..."
    gunicorn -w 4 -b 0.0.0.0:${PORT} boot:create_app \
        --access-logfile - \
        --error-logfile - &
    GUNICORN_PID=$!
    log_success "ᴠx ᴀᴘɪ ꜱᴇʀᴠᴇʀ ʀᴜɴɴɪɴɢ ᴏɴ ᴘᴏʀᴛ ${PORT} (ᴘɪᴅ: ${GUNICORN_PID})"

    sleep 2 

    log_info "ɪɴɪᴛɪᴀʟɪᴢɪɴɢ ᴠx ᴀɪ ᴄᴏʀᴇ ᴇɴɢɪɴᴇ..."
    python3 -m Opus &
    VX_PID=$!
    log_success "ᴠx ᴀɪ ᴄᴏʀᴇ ᴇɴɢɪɴᴇ ꜱᴛᴀʀᴛᴇᴅ (ᴘɪᴅ: ${VX_PID})"

    log_success "ᴠx ᴀɪ ꜱʏꜱᴛᴇᴍ ɪɴɪᴛɪᴀʟɪᴢᴀᴛɪᴏɴ ᴄᴏᴍᴘʟᴇᴛᴇ"
    log_info "ᴀʟʟ ꜱᴇʀᴠɪᴄᴇꜱ ʀᴜɴɴɪɴɢ - ᴘʀᴇꜱꜱ ᴄᴛʀʟ+ᴄ ᴛᴏ ꜱʜᴜᴛᴅᴏᴡɴ"

    wait ${GUNICORN_PID} ${VX_PID} || true
    log_error "ᴀ ꜱᴇʀᴠɪᴄᴇ ʜᴀꜱ ꜱᴛᴏᴘᴘᴇᴅ ᴜɴᴇxᴘᴇᴄᴛᴇᴅʟʏ"
    cleanup
}

trap cleanup SIGINT SIGTERM

start_services
