import {Link} from 'react-router-dom';
import { FaHome, FaFacebook, FaTwitter, FaInstagram } from "react-icons/fa";
import { TfiYoutube } from "react-icons/tfi";
import ReactPlayer from "react-player";
import "bootstrap/dist/css/bootstrap.min.css";
import './index.css';
import NavigationBar from '../Navbar';

export default function Home() {
  return (
      <div className="flex flex-col items-center justify-center p-6 home">
      <NavigationBar/>
      <ReactPlayer 
      url="https://webfiles.amrita.edu/2024/06/amrita-campus-video-home-page.mp4"
      playing={true}    // Autoplay enabled
      muted={true}      // Muted by default
      loop={true}       // Looping enabled
      playsinline={true} // For mobile compatibility
      controls={false}   // Hide controls (Set to true to show)
      width="100%"       // Full width
      height="auto" 
    />
    <div className='foot'>
      <div className="mt-8 text-center contai">
        <img src="https://webfiles.amrita.edu/2024/04/WhQq1FiB-amrita-vishwa-vidyapeetham-university-logo-colored-version.svg" alt="contacts-logo"/>
        <div className='con'>
          <h4 className="text-lg font-semibold">Contact Us</h4>
          <div className='cc'>
            <div className='mail'>
              <img className='img' src="https://www.amrita.edu/wp-content/themes/amrita/images/phone.svg" alt="Phone" />
              <a className='a' href="tel:04446276066">044-462-76066</a>
            </div>
            <div className='phone'>
              <img className='img' src="https://www.amrita.edu/wp-content/themes/amrita/images/mail.svg" alt="" />
              <a className='a' href="mailto:btech@amrita.edu">btech@amrita.edu</a>
            </div>
        </div>
      </div>
    </div>

      <div className="mt-2 socials text-center">
          <Link to="https://www.facebook.com/AmritaUniversity/"><FaFacebook className="text-blue-600 text-2xl mx-2 cursor-pointer icons" /></Link>
          <Link to="https://x.com/AMRITAedu?mx=2"><FaTwitter className="text-blue-400 text-2xl mx-2 cursor-pointer icons" /></Link>
          <Link to="https://www.instagram.com/amrita_university/"><FaInstagram className="text-pink-500 text-2xl mx-2 cursor-pointer icons" /></Link>
          <Link to="https://www.youtube.com/user/AmritaUniversity"><TfiYoutube className='mx-2 cursor-pointer icons'/></Link>
        </div>      
        </div>
    </div>
  );
}
