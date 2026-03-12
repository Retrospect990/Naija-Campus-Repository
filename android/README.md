# Campus Pinduoduo Android App

Complete Android interface for the Campus Pinduoduo group shopping and escrow platform.

## 📱 Features

### Core Functionality
- **Product Browsing**: Browse all products with filtering by category, brand, and price
- **Shopping Cart**: Add items to cart with budget tracking
- **Budget Management**: Real-time display of remaining pool budget
- **Order Placement**: Place orders with moderator verification
- **Order Tracking**: Track order status and delivery confirmation
- **User Profile**: Manage user information and view statistics

### Technical Stack
- **Language**: Kotlin
- **Architecture**: MVVM (Model-View-ViewModel)
- **UI Framework**: AndroidX
- **Networking**: Retrofit 2 with OkHttp
- **Serialization**: Gson
- **Lifecycle**: LiveData & ViewModel

## 📂 Project Structure

```
android/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/campuspinduoduo/
│   │   │   │   ├── ui/
│   │   │   │   │   ├── activities/          # Screen implementations
│   │   │   │   │   ├── fragments/          # Fragment components
│   │   │   │   │   └── adapters/           # RecyclerView adapters
│   │   │   │   ├── viewmodel/              # ViewModel classes
│   │   │   │   ├── api/                    # Retrofit API service
│   │   │   │   └── model/                  # Data models
│   │   │   ├── res/
│   │   │   │   ├── layout/                 # XML layouts
│   │   │   │   ├── values/                 # Resources (strings, colors)
│   │   │   │   ├── menu/                   # Menu definitions
│   │   │   │   └── drawable/               # Drawable resources
│   │   │   └── AndroidManifest.xml
│   │   └── test/                           # Unit tests
│   └── build.gradle
├── build.gradle
└── settings.gradle
```

## 🚀 Getting Started

### Prerequisites
- Android Studio 2022.3 or later
- Android SDK 24 (min) - 34 (target)
- Kotlin 1.9+
- Gradle 8.1+

### Installation

1. **Clone the repository**
```bash
git clone <repository_url>
cd android
```

2. **Open in Android Studio**
   - File → Open → Select the `android` folder
   - Let Gradle sync automatically

3. **Configure API Endpoint**
   - Edit `api/RetrofitClient.kt`
   - Change `BASE_URL` to your backend server:
   ```kotlin
   // For emulator: http://10.0.2.2:5000/
   // For real device: http://<YOUR_SERVER_IP>:5000/
   private const val BASE_URL = "http://10.0.2.2:5000/"
   ```

4. **Build & Run**
   - Connect Android device or start emulator
   - Click "Run" or press `Shift + F10`

## 📱 Activities & Screens

### MainActivity
- **Purpose**: Product catalog and shopping
- **Features**:
  - Search products by name
  - Filter by category
  - Grid view of products (2 columns)
  - Navigation to cart and orders

### ProductDetailActivity
- **Purpose**: Detailed product information
- **Features**:
  - Full product description
  - Rating and reviews
  - Available quantity
  - Add to cart with quantity selector

### CartActivity
- **Purpose**: Review and manage shopping cart
- **Features**:
  - List of cart items
  - Item quantities and prices
  - Remove items
  - Budget remaining display
  - Checkout button

### CheckoutActivity
- **Purpose**: Complete the order
- **Features**:
  - Order summary
  - Budget information
  - Moderator ID verification
  - Order confirmation

### OrderTrackingActivity
- **Purpose**: Track order status
- **Features**:
  - List of user orders
  - Order status display
  - Order dates and amounts
  - Delivery tracking

### ProfileActivity
- **Purpose**: User account management
- **Features**:
  - Edit name, email, phone
  - View order history stats
  - View total spent
  - View user rating

## 🔌 API Integration

### Configured Endpoints

**Product Endpoints**
- `GET /api/store/products` - List all products
- `GET /api/store/products/{id}` - Product details
- `GET /api/store/categories` - List categories

**Cart Endpoints**
- `GET /api/store/cart/{pool_id}` - Get cart
- `POST /api/store/cart/{pool_id}/add` - Add item
- `POST /api/store/cart/{pool_id}/remove` - Remove item
- `POST /api/store/cart/{pool_id}/clear` - Clear cart

**Order Endpoints**
- `POST /api/store/orders/place` - Place order
- `GET /api/store/orders/{order_id}` - Get order details
- `GET /api/store/orders/user/{user_id}` - User orders
- `POST /api/store/delivery/{order_id}/confirm` - Confirm delivery

**Pool Endpoints**
- `GET /api/pools` - List all pools
- `GET /api/pools/{pool_id}` - Pool details
- `POST /api/pools/{pool_id}/join` - Join pool

## 🎨 UI/UX Design

### Color Scheme
- **Primary**: #1F77D2 (Blue)
- **Accent**: #FF6B35 (Orange)
- **Price**: #D32F2F (Red)
- **Success**: #4CAF50 (Green)

### Layouts
- Product Grid: 2-column responsive layout
- Lists: LinearLayout with RecyclerView
- Details: ScrollView for overflow content
- Forms: Input validation with error messages

## 📦 Dependencies

### Build Tools
- Gradle: 8.1.0
- Android Gradle Plugin: 8.1.0

### Libraries
- AndroidX AppCompat: 1.6.1
- Material Design: 1.9.0
- Retrofit 2: 2.9.0
- Gson: 2.10.1
- OkHttp: 4.11.0
- Lifecycle Components: 2.6.1
- RecyclerView: 1.3.1
- Glide (for images): 4.15.1

## 🔐 Security Considerations

1. **API Communication**
   - Use HTTPS in production
   - Implement certificate pinning for sensitive data

2. **Data Storage**
   - Store tokens securely in SharedPreferences with encryption
   - Avoid storing sensitive data in plain text

3. **Authentication**
   - Implement JWT token-based authentication
   - Auto-refresh tokens before expiration

## 🧪 Testing

### Run Unit Tests
```bash
./gradlew test
```

### Run Instrumentation Tests
```bash
./gradlew connectedAndroidTest
```

## 📥 Building for Release

```bash
# Build signed APK
./gradlew bundleRelease

# Build APK
./gradlew assembleRelease
```

## 🤝 Integration with Backend

The Android app is fully integrated with the Campus Pinduoduo backend:

1. **Product Management**: Browse products persisted in backend database
2. **Cart Management**: Server-side validation of budget constraints
3. **Order Processing**: Complete order lifecycle tracking
4. **Delivery Confirmation**: PIN-based delivery verification
5. **Escrow System**: Automatic fund release on confirmation threshold

## 📝 Configuration

### Server Configuration
Update `RetrofitClient.kt`:
```kotlin
private const val BASE_URL = "http://your-server-ip:5000/"
```

### Timeouts
```kotlin
.connectTimeout(30, TimeUnit.SECONDS)
.readTimeout(30, TimeUnit.SECONDS)
.writeTimeout(30, TimeUnit.SECONDS)
```

## 🐛 Troubleshooting

### App crashes on startup
- Check `BASE_URL` in `RetrofitClient.kt`
- Ensure backend server is running
- Verify network connectivity

### Cart not loading
- Enable network logging: Check logcat for API responses
- Verify pool ID is set correctly

### Order placement fails
- Check moderator ID format
- Ensure budget is sufficient
- Verify backend order service is running

## 📞 Support

For issues or questions:
1. Check the backend API documentation
2. Review logcat for detailed error messages
3. Verify network connectivity
4. Check backend server status

## 📄 License

Campus Pinduoduo Android App - All Rights Reserved

## 🎯 Future Enhancements

- [ ] Biometric authentication (fingerprint/face)
- [ ] Push notifications for order updates
- [ ] In-app messaging between moderator and members
- [ ] Payment gateway integration
- [ ] Splash screen and onboarding
- [ ] Offline mode with sync
- [ ] Widget for quick cart access
- [ ] Dark mode support
